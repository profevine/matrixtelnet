import asyncio
import random
import time
import shutil
import os
from matrix_rain import MatrixRain, GREEN, BRIGHT_GREEN, RESET, CLEAR, HIDE_CURSOR, SHOW_CURSOR

# ANSI for progress bar and controls
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
    """Streams frames from a file with seeking support using a byte index."""
    def __init__(self, file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.full_path = os.path.join(base_dir, file_path)
        self.offsets = []
        self._index_file()

    def _index_file(self):
        if not os.path.exists(self.full_path):
            return
        print(f"Indexing {self.full_path}...")
        with open(self.full_path, 'rb') as f:
            offset = 0
            for line in f:
                if line.startswith(b'====='):
                    self.offsets.append(offset)
                offset += len(line)
        print(f"Indexed {len(self.offsets)} frames.")

    def get_frame(self, index):
        if not self.offsets or index >= len(self.offsets):
            return None
        
        index = max(0, min(index, len(self.offsets) - 1))
        with open(self.full_path, 'r') as f:
            f.seek(self.offsets[index])
            f.readline() # Skip the ===== line
            current_frame = []
            for line in f:
                if line.startswith('====='):
                    break
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
        width = 40
        progress = int((current / total) * width) if total > 0 else 0
        bar = "█" * progress + "-" * (width - progress)
        percent = (current / total) * 100 if total > 0 else 0
        
        # Format time MM:SS
        cur_time = f"{int(current/24//60):02d}:{int(current/24%60):02d}"
        tot_time = f"{int(total/24//60):02d}:{int(total/24%60):02d}"
        
        return f"\r{tot_time} [{BLUE}{bar}{RESET}] {cur_time} ({percent:.1f}%)"

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")
        
        try:
            writer.write(HIDE_CURSOR.encode() + CLEAR.encode() + WELCOME.encode())
            await writer.drain()
            await asyncio.sleep(3)
            
            frame_idx = 0
            playing = True
            total_frames = len(self.movie)
            
            # Task to read input from client
            async def get_input():
                nonlocal frame_idx, playing
                while True:
                    try:
                        data = await reader.read(1)
                        if not data: break
                        key = data.decode().lower()
                        
                        if key == ' ': # Pause/Play
                            playing = not playing
                        elif key == 'l': # +10s (approx 240 frames)
                            frame_idx = min(frame_idx + 240, total_frames - 1)
                        elif key == 'h': # -10s
                            frame_idx = max(frame_idx - 240, 0)
                        elif key == 'j': # +1m (1440 frames)
                            frame_idx = min(frame_idx + 1440, total_frames - 1)
                        elif key == 'k': # -1m
                            frame_idx = max(frame_idx - 1440, 0)
                        elif key == 'q': # Quit
                            break
                    except: break

            input_task = asyncio.create_task(get_input())
            
            while frame_idx < total_frames:
                if playing:
                    frame = self.movie.get_frame(frame_idx)
                    if frame:
                        progress = self.get_progress_bar(frame_idx, total_frames)
                        # Clear screen, show frame, then progress bar at bottom
                        writer.write((CLEAR + frame + "\n\n" + progress).encode())
                        await writer.drain()
                        frame_idx += 1
                    await asyncio.sleep(0.04) # 24 FPS
                else:
                    # Paused state: just update the progress bar to show PAUSED
                    progress = self.get_progress_bar(frame_idx, total_frames)
                    writer.write(f"\r{progress} [PAUSED]".encode())
                    await writer.drain()
                    await asyncio.sleep(0.5)

            input_task.cancel()
            
            # Infinite Matrix Rain after movie
            rain = MatrixRain(80, 24)
            while True:
                rain.update()
                writer.write(rain.get_frame().encode())
                await writer.drain()
                await asyncio.sleep(0.05)
                
        except (ConnectionResetError, BrokenPipeError):
            print(f"Connection closed by {addr}")
        except Exception as e:
            print(f"Error handling {addr}: {e}")
        finally:
            try:
                writer.write(RESET.encode() + SHOW_CURSOR.encode())
                writer.close()
                await writer.wait_closed()
            except: pass

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f'Serving on port {self.port}')
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = MatrixTelnetServer()
    asyncio.run(server.start())
