import asyncio
import random
import time
import shutil
import os
from matrix_rain import MatrixRain, GREEN, BRIGHT_GREEN, RESET, CLEAR, HIDE_CURSOR, SHOW_CURSOR

WELCOME = fr"""{BRIGHT_GREEN}
WELCOME TO THE DESERT OF THE REAL.

  _   _             
 | \ | | ___  ___  
 |  \| |/ _ \/ _ \ 
 | |\  |  __/ (_) |
 |_| \_|\___|\___/ 

Connecting to the Matrix...
{RESET}"""

class FrameStreamer:
    """Streams frames from a file without loading it entirely into memory."""
    def __init__(self, file_path):
        self.file_path = file_path
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.full_path = os.path.join(self.base_dir, file_path)

    def frames(self):
        if not os.path.exists(self.full_path):
            return
        
        with open(self.full_path, 'r') as f:
            current_frame = []
            for line in f:
                if line.startswith('====='):
                    if current_frame:
                        yield "".join(current_frame).strip()
                        current_frame = []
                else:
                    current_frame.append(line)
            if current_frame:
                yield "".join(current_frame).strip()

class MatrixTelnetServer:
    def __init__(self, host='0.0.0.0', port=2772):
        self.host = host
        self.port = port

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")
        
        try:
            writer.write(HIDE_CURSOR.encode())
            writer.write(CLEAR.encode())
            writer.write(WELCOME.encode())
            await writer.drain()
            await asyncio.sleep(3)
            
            # 1. Play "story.txt" (Classic Slow Scenes)
            story_streamer = FrameStreamer("frames/story.txt")
            for frame in story_streamer.frames():
                writer.write((CLEAR + BRIGHT_GREEN + frame + RESET).encode())
                await writer.drain()
                await asyncio.sleep(3)
            
            # 2. Play "movie_sequence.txt" (High FPS Streaming)
            movie_streamer = FrameStreamer("frames/movie_sequence.txt")
            for frame in movie_streamer.frames():
                writer.write((CLEAR + BRIGHT_GREEN + frame + RESET).encode())
                await writer.drain()
                await asyncio.sleep(0.04) # ~24 FPS
            
            # 3. Infinite Matrix Rain
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
