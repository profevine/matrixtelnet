"""
DISCLAIMER: This project is for educational purposes only and has no commercial intent.
"The Matrix" is a registered trademark of Warner Bros. Entertainment Inc.
"""

import argparse
import asyncio
import logging
import os
import pickle
import signal
import time

from matrix_rain import MatrixRain, BRIGHT_GREEN, RESET, CLEAR, HIDE_CURSOR, SHOW_CURSOR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger(__name__)

# Telnet protocol constants (RFC 854 / RFC 1073)
IAC  = 0xFF
WILL = 0xFB
WONT = 0xFC
DO   = 0xFD
DONT = 0xFE
SB   = 0xFA
SE   = 0xF0
ECHO = 0x01
SGA  = 0x03
NAWS = 0x1F  # Negotiate About Window Size (RFC 1073)

FPS             = 24
MAX_CONNECTIONS = 50
DEFAULT_WIDTH   = 80
DEFAULT_HEIGHT  = 24

BLUE = "\033[94m"

WELCOME = fr"""{BRIGHT_GREEN}
WELCOME TO THE DESERT OF THE REAL.

  _   _
 | \ | | ___  ___
 |  \| |/ _ \/ _ \
 | |\  |  __/ (_) |
 |_| \_|\___|\___/

Connecting to the Matrix...
Controls: [Space] Play/Pause | [L] +10s | [H] -10s | [J] +1m | [K] -1m | [Q] Quit
{RESET}"""


class IndexedFrameStreamer:
    def __init__(self, file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.full_path = os.path.join(base_dir, file_path)
        self.index_path = self.full_path + ".idx"
        self.offsets = []
        self.is_ready = False

    async def ensure_indexed(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'rb') as f:
                    self.offsets = pickle.load(f)
                self.is_ready = True
                log.info("Loaded frame index: %d frames", len(self.offsets))
                return
            except Exception as e:
                log.warning("Failed to load index cache: %s — rebuilding", e)

        log.info("Building frame index for %s...", self.full_path)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._index_file)
        self.is_ready = True
        log.info("Index built: %d frames", len(self.offsets))

    def _index_file(self):
        if not os.path.exists(self.full_path):
            log.error("Frame file not found: %s", self.full_path)
            return
        offsets = []
        with open(self.full_path, 'rb') as f:
            offset = 0
            while True:
                line = f.readline()
                if not line:
                    break
                if line.startswith(b'====='):
                    offsets.append(offset)
                offset += len(line)
        self.offsets = offsets
        try:
            with open(self.index_path, 'wb') as f:
                pickle.dump(offsets, f)
        except Exception as e:
            log.warning("Could not save index cache: %s", e)

    def open_reader(self):
        """Open a dedicated file handle for one client."""
        return open(self.full_path, 'r', encoding='utf-8', errors='ignore')

    def get_frame(self, fd, index):
        if not self.offsets or index >= len(self.offsets):
            return None
        index = max(0, min(index, len(self.offsets) - 1))
        fd.seek(self.offsets[index])
        fd.readline()  # skip the ===== separator line
        lines = []
        for line in fd:
            if line.startswith('====='):
                break
            lines.append(line)
        return "".join(lines).strip().replace('\n', '\r\n')

    def __len__(self):
        return len(self.offsets)


class MatrixTelnetServer:
    def __init__(self, host='0.0.0.0', port=2772,
                 movie_path='frames/movie_sequence.txt',
                 max_connections=MAX_CONNECTIONS):
        self.host = host
        self.port = port
        self.movie = IndexedFrameStreamer(movie_path)
        self.max_connections = max_connections
        self.active_connections = 0

    def _progress_bar(self, current, total, width):
        if total == 0:
            return "[INDEXING...]"
        bar_width = max(10, min(40, width - 25))
        filled = int((current / total) * bar_width)
        bar = "█" * filled + "-" * (bar_width - filled)
        cur = f"{int(current / FPS // 60):02d}:{int(current / FPS % 60):02d}"
        tot = f"{int(total / FPS // 60):02d}:{int(total / FPS % 60):02d}"
        return f"\r{cur} [{BLUE}{bar}{RESET}] {tot} ({current / total * 100:.1f}%)"

    async def _negotiate(self, reader, writer):
        """Send initial Telnet options and return (width, height) via NAWS or defaults."""
        writer.write(bytes([
            IAC, WILL, ECHO,
            IAC, WILL, SGA,
            IAC, DO,   SGA,
            IAC, DO,   NAWS,
        ]))
        await writer.drain()

        async def _read_naws():
            w, h = DEFAULT_WIDTH, DEFAULT_HEIGHT
            while True:
                data = await reader.read(1)
                if not data:
                    return w, h
                if data[0] != IAC:
                    continue
                cmd = await reader.read(1)
                if not cmd:
                    return w, h
                c = cmd[0]
                if c == SB:
                    opt = await reader.read(1)
                    if not opt:
                        return w, h
                    if opt[0] == NAWS:
                        dims = await reader.read(4)
                        if len(dims) == 4:
                            w = max(40, (dims[0] << 8) | dims[1])
                            h = max(10, (dims[2] << 8) | dims[3])
                        await reader.read(2)  # IAC SE
                        return w, h
                    else:
                        # Unknown subnegotiation — consume until IAC SE
                        while True:
                            b = await reader.read(1)
                            if not b:
                                return w, h
                            if b[0] == IAC:
                                se = await reader.read(1)
                                if se and se[0] == SE:
                                    break
                elif c in (WILL, WONT, DO, DONT):
                    opt = await reader.read(1)
                    if opt and c == WONT and opt[0] == NAWS:
                        return w, h  # client refused NAWS

        try:
            return await asyncio.wait_for(_read_naws(), timeout=2.0)
        except asyncio.TimeoutError:
            return DEFAULT_WIDTH, DEFAULT_HEIGHT

    async def _read_key(self, reader):
        """Read one user keypress, consuming any Telnet IAC sequences transparently."""
        while True:
            data = await reader.read(1)
            if not data:
                return None
            b = data[0]
            if b != IAC:
                return b
            cmd = await reader.read(1)
            if not cmd:
                return None
            c = cmd[0]
            if c == SB:
                while True:
                    x = await reader.read(1)
                    if not x:
                        return None
                    if x[0] == IAC:
                        se = await reader.read(1)
                        if se and se[0] == SE:
                            break
            elif c in (WILL, WONT, DO, DONT):
                await reader.read(1)

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        if self.active_connections >= self.max_connections:
            log.warning("Connection refused (limit %d reached): %s", self.max_connections, addr)
            writer.close()
            return

        self.active_connections += 1
        log.info("Connected: %s  (active: %d)", addr, self.active_connections)

        quit_event = asyncio.Event()
        fd = None
        try:
            term_w, term_h = await self._negotiate(reader, writer)
            log.info("Terminal %dx%d for %s", term_w, term_h, addr)

            writer.write(HIDE_CURSOR.encode() + CLEAR.encode() + WELCOME.replace('\n', '\r\n').encode())
            await writer.drain()

            while not self.movie.is_ready:
                writer.write(b"\rBuilding index, please wait...\r\n")
                await writer.drain()
                await asyncio.sleep(2)

            fd = self.movie.open_reader()
            frame_idx = 0
            playing = True
            total = len(self.movie)

            async def get_input():
                nonlocal frame_idx, playing
                try:
                    while not quit_event.is_set():
                        b = await self._read_key(reader)
                        if b is None:
                            quit_event.set()
                            return
                        key = chr(b).lower()
                        if key == ' ':
                            playing = not playing
                        elif key == 'l':
                            frame_idx = min(frame_idx + FPS * 10, total - 1)
                        elif key == 'h':
                            frame_idx = max(frame_idx - FPS * 10, 0)
                        elif key == 'j':
                            frame_idx = min(frame_idx + FPS * 60, total - 1)
                        elif key == 'k':
                            frame_idx = max(frame_idx - FPS * 60, 0)
                        elif key == 'q':
                            quit_event.set()
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    log.debug("Input error for %s: %s", addr, e)
                    quit_event.set()

            input_task = asyncio.create_task(get_input())

            # Movie playback
            while frame_idx < total and not quit_event.is_set():
                if playing:
                    t0 = time.monotonic()
                    frame = self.movie.get_frame(fd, frame_idx)
                    if frame:
                        progress = self._progress_bar(frame_idx, total, term_w)
                        writer.write((CLEAR + frame + "\r\n\r\n" + progress).encode())
                        await writer.drain()
                        frame_idx += 1
                    sleep = max(0.0, 1 / FPS - (time.monotonic() - t0))
                    await asyncio.sleep(sleep) if sleep > 0 else await asyncio.sleep(0)
                else:
                    progress = self._progress_bar(frame_idx, total, term_w)
                    writer.write(f"{progress} [PAUSED]".encode())
                    await writer.drain()
                    await asyncio.sleep(0.5)

            # Matrix rain (runs until client quits or disconnects)
            if not quit_event.is_set():
                rain = MatrixRain(term_w, term_h)
                while not quit_event.is_set():
                    t0 = time.monotonic()
                    rain.update()
                    writer.write(rain.get_frame().replace('\n', '\r\n').encode())
                    await writer.drain()
                    sleep = max(0.0, 0.05 - (time.monotonic() - t0))
                    await asyncio.sleep(sleep) if sleep > 0 else await asyncio.sleep(0)

            input_task.cancel()
            try:
                await input_task
            except asyncio.CancelledError:
                pass

        except (BrokenPipeError, ConnectionResetError, asyncio.IncompleteReadError):
            pass
        except Exception as e:
            log.error("Unexpected error for %s: %s", addr, e)
        finally:
            if fd:
                fd.close()
            try:
                writer.write(RESET.encode() + SHOW_CURSOR.encode())
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            self.active_connections -= 1
            log.info("Disconnected: %s  (active: %d)", addr, self.active_connections)

    async def start(self):
        asyncio.create_task(self.movie.ensure_indexed())
        server = await asyncio.start_server(self.handle_client, self.host, self.port)

        loop = asyncio.get_running_loop()

        def _shutdown():
            log.info("Shutdown signal received.")
            server.close()

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, _shutdown)

        log.info("Matrix Telnet Server on %s:%d  (max connections: %d)",
                 self.host, self.port, self.max_connections)
        async with server:
            await server.serve_forever()
        log.info("Server stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matrix ASCII Telnet Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=2772, help="Port number")
    parser.add_argument("--movie", default="frames/movie_sequence.txt", help="Path to frames file")
    parser.add_argument("--max-connections", type=int, default=MAX_CONNECTIONS,
                        help="Max simultaneous clients")
    args = parser.parse_args()

    asyncio.run(MatrixTelnetServer(args.host, args.port, args.movie, args.max_connections).start())
