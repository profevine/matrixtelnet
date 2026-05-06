# Matrix Telnet Server

Inspired by `towel.blinkenlights.nl`, this server plays a Matrix-themed experience in ASCII art.

## Features
- **Story Mode:** Iconic scenes from the movie in ASCII.
- **Matrix Rain:** The classic digital rain effect.
- **TCP Server:** Listen on port 2772 for incoming connections.

## How to run locally
1. Ensure you have Python 3 installed.
2. Run the server:
   ```bash
   python3 matrix_telnet/server.py
   ```
3. Connect from another terminal:
   ```bash
   telnet localhost 2772
   # or
   nc localhost 2772
   ```

## Deploying to Raspberry Pi
To run this permanently on your Raspberry Pi:

1. Copy the `matrix_telnet` folder to your Pi.
2. Run the setup script:
   ```bash
   bash setup_pi.sh
   ```
   This will create a systemd service named `matrix-telnet.service` that starts automatically on boot.

## Adding More Movie Frames
You can add more frames to `matrix_telnet/frames/story.txt`. Use `=====` as a delimiter between frames.
The server will play them in sequence before starting the Matrix Rain.
