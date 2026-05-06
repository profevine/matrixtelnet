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
    def __init__(self, file_path):
        self.frames = []
        # Use absolute path based on script location to avoid issues
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, "frames", "story.txt")
        
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                # Split by ===== and filter out empty frames
                self.frames = [f.strip() for f in content.split('=====') if f.strip()]
        else:
            print(f"Warning: Frame file not found at {full_path}")

    def get_frame(self, frame_index):
        if not self.frames:
            return ""
        frame = self.frames[frame_index % len(self.frames)]
        return CLEAR + BRIGHT_GREEN + frame + RESET

class MatrixTelnetServer:
    def __init__(self, host='0.0.0.0', port=2772):
        self.host = host
        self.port = port
        self.movie = MoviePlayer('frames/story.txt')

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")
        
        try:
            writer.write(HIDE_CURSOR.encode())
            writer.write(CLEAR.encode())
            writer.write(WELCOME.encode())
            await writer.drain()
            await asyncio.sleep(3)
            
            rain = MatrixRain(80, 24)
            scene_index = 0
            
            while True:
                # 1. Play a scene from the movie
                if self.movie.frames:
                    frame = self.movie.get_frame(scene_index)
                    writer.write(frame.encode())
                    await writer.drain()
                    await asyncio.sleep(4) # Show scene for 4 seconds
                    scene_index += 1
                
                # 2. Play Matrix Rain for a bit
                start_rain = time.time()
                while time.time() - start_rain < 10: # 10 seconds of rain
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
            except:
                pass

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f'Serving on port {self.port}')
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = MatrixTelnetServer()
    asyncio.run(server.start())
