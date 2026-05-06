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

class MoviePlayer:
    def __init__(self, folder_path):
        self.sequences = {}
        base_dir = os.path.dirname(os.path.abspath(__file__))
        frames_dir = os.path.join(base_dir, "frames")
        
        if os.path.exists(frames_dir):
            for filename in os.listdir(frames_dir):
                if filename.endswith(".txt"):
                    path = os.path.join(frames_dir, filename)
                    with open(path, 'r') as f:
                        content = f.read()
                        frames = [fr.strip() for fr in content.split('=====') if fr.strip()]
                        self.sequences[filename] = frames

    def get_sequence(self, name):
        return self.sequences.get(name, [])

class MatrixTelnetServer:
    def __init__(self, host='0.0.0.0', port=2772):
        self.host = host
        self.port = port
        self.movie = MoviePlayer('frames')

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
            story = self.movie.get_sequence("story.txt")
            for frame in story:
                writer.write((CLEAR + BRIGHT_GREEN + frame + RESET).encode())
                await writer.drain()
                await asyncio.sleep(3)
            
            # 2. Play "movie_sequence.txt" (High FPS converted video)
            video = self.movie.get_sequence("movie_sequence.txt")
            for frame in video:
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
