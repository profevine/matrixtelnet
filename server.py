import asyncio
import random
import time
import shutil
import os
import pickle
from matrix_rain import MatrixRain, GREEN, BRIGHT_GREEN, RESET, CLEAR, HIDE_CURSOR, SHOW_CURSOR

# Telnet Protocol Constants
IAC  = b'\xff' # Interpret As Command
WILL = b'\xfb'
WONT = b'\xfc'
DO   = b'\xfd'
DONT = b'\xfe'
ECHO = b'\x01'
SGA  = b'\x03' # Suppress Go Ahead

YELLOW = "\033[93m"
BLUE = "\033[94m"

WELCOME = fr"""{BRIGHT_GREEN}
WELCOME TO THE DESERT OF THE REAL.

  _   _             
 | \ | | ___  ___  
 |  \| |/ _ \/ _ \ 
 | |\  |  __/ (_) |
 |_| \_|\___|\___/ 

Connecting to the Matrix...
Controls: [Space] Play/Pause | [L] +10s | [H] -10s | [J] +1m | [K] -1m
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
                return
            except: pass

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._index_file)
        self.is_ready = True

    def _index_file(self):
        if not os.path.exists(self.full_path): return
        offsets = []
        with open(self.full_path, 'rb') as f:
            offset = 0
            while True:
                line = f.readline()
                if not line: break
                if line.startswith(b'====='):
                    offsets.append(offset)
                offset += len(line)
        self.offsets = offsets
        try:
            with open(self.index_path, 'wb') as f:
                pickle.dump(offsets, f)
        except: pass

    def get_frame(self, index):
        if not self.offsets or index >= len(self.offsets): return None
        index = max(0, min(index, len(self.offsets) - 1))
        with open(self.full_path, 'r', encoding='utf-8', errors='ignore') as f:
            f.seek(self.offsets[index])
            f.readline()
            current_frame = []
            for line in f:
                if line.startswith('====='): break
                current_frame.append(line)
            return "".join(current_frame).strip()

    def __len__(self):
        return len(self.offsets)

class MatrixTelnetServer:
    def __init__(self, host='0.0.0.0', port=2772):
        self.host = host
        self.port = port
        self.movie = IndexedFrameStreamer("frames/movie_sequence.txt")

    def get_progress_bar(self, current, total):
        if total == 0: return "[INDEXING...]"
        width = 40
        progress = int((current / total) * width)
        bar = "█" * progress + "-" * (width - progress)
        cur_time = f"{int(current/24//60):02d}:{int(current/24%60):02d}"
        tot_time = f"{int(total/24//60):02d}:{int(total/24%60):02d}"
        return f"\r{tot_time} [{BLUE}{bar}{RESET}] {cur_time} ({ (current/total)*100:.1f}%)"

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        try:
            # TELNET NEGOTIATION: Request Character Mode
            # We tell the client: "I will echo, I will suppress go-ahead, you should suppress go-ahead"
            writer.write(IAC + WILL + ECHO)
            writer.write(IAC + WILL + SGA)
            writer.write(IAC + DO + SGA)
            await writer.drain()

            writer.write(HIDE_CURSOR.encode() + CLEAR.encode() + WELCOME.encode())
            await writer.drain()
            
            while not self.movie.is_ready:
                writer.write(b"\rBuilding Index... Please wait.\r")
                await writer.drain()
                await asyncio.sleep(2)
            
            frame_idx = 0
            playing = True
            total_frames = len(self.movie)
            
            async def get_input():
                nonlocal frame_idx, playing
                while True:
                    data = await reader.read(1)
                    if not data: break
                    # Ignore telnet commands (starting with \xff)
                    if data[0] == 255:
                        # Skip next 2 bytes of telnet command
                        await reader.read(2)
                        continue
                        
                    key = data.decode().lower()
                    if key == ' ': playing = not playing
                    elif key == 'l': frame_idx = min(frame_idx + 240, total_frames - 1)
                    elif key == 'h': frame_idx = max(frame_idx - 240, 0)
                    elif key == 'j': frame_idx = min(frame_idx + 1440, total_frames - 1)
                    elif key == 'k': frame_idx = max(frame_idx - 1440, 0)
                    elif key == 'q': break
            
            input_task = asyncio.create_task(get_input())
            
            while frame_idx < total_frames:
                if playing:
                    frame = self.movie.get_frame(frame_idx)
                    if frame:
                        progress = self.get_progress_bar(frame_idx, total_frames)
                        writer.write((CLEAR + frame + "\n\n" + progress).encode())
                        await writer.drain()
                        frame_idx += 1
                    await asyncio.sleep(0.04)
                else:
                    progress = self.get_progress_bar(frame_idx, total_frames)
                    writer.write(f"\r{progress} [PAUSED]".encode())
                    await writer.drain()
                    await asyncio.sleep(0.5)
            
            input_task.cancel()
            rain = MatrixRain(80, 24)
            while True:
                rain.update()
                writer.write(rain.get_frame().encode())
                await writer.drain()
                await asyncio.sleep(0.05)
                
        except: pass
        finally:
            try:
                writer.write(RESET.encode() + SHOW_CURSOR.encode())
                writer.close()
                await writer.wait_closed()
            except: pass

    async def start(self):
        asyncio.create_task(self.movie.ensure_indexed())
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f'Serving on port {self.port}')
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = MatrixTelnetServer()
    asyncio.run(server.start())
