import asyncio
import random
import time
import shutil
import os
from matrix_rain import MatrixRain, GREEN, BRIGHT_GREEN, RESET, CLEAR, HIDE_CURSOR, SHOW_CURSOR

# Welcome message
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
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                self.frames = content.split('=====')[1:] # Skip first empty split if any

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
            # Send hide cursor command
            writer.write(HIDE_CURSOR.encode())
            writer.write(CLEAR.encode())
            
            # Send welcome
            writer.write(WELCOME.encode())
            await writer.drain()
            await asyncio.sleep(3)
            
            # Story Mode
            if self.movie.frames:
                for i in range(len(self.movie.frames)):
                    frame = self.movie.get_frame(i)
                    writer.write(frame.encode())
                    await writer.drain()
                    await asyncio.sleep(2) # 2 seconds per scene
            
            # Infinite Rain Mode
            width, height = 80, 24
            rain = MatrixRain(width, height)
            
            while True:
                rain.update()
                frame = rain.get_frame()
                
                writer.write(frame.encode())
                await writer.drain()
                
                await asyncio.sleep(0.05)
                
        except (ConnectionResetError, BrokenPipeError):
            print(f"Connection closed by {addr}")
        except Exception as e:
            print(f"Error handling {addr}: {e}")
        finally:
            try:
                writer.write(SHOW_CURSOR.encode())
                writer.close()
                await writer.wait_closed()
            except:
                pass

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = MatrixTelnetServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nServer shutting down.")
