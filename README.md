# Matrix ASCII Telnet Server 🕶️

Inspired by the famous `towel.blinkenlights.nl`, this project brings the Matrix experience to your terminal. It serves an ASCII version of the movie story, followed by high-FPS converted video sequences, and finally the iconic infinite "Digital Rain" effect—all over a TCP connection (Telnet).

## ✨ Features

- **Story Mode:** Displays key scenes from "The Matrix" in stylized ASCII art (slow-paced).
- **Video Playback:** Support for 24 FPS ASCII video sequences.
- **Infinite Matrix Rain:** The classic falling green code effect.
- **Video-to-ASCII Converter:** A built-in tool to transform any `.mp4` into terminal art.
- **Telnet/TCP Server:** Lightweight server using Python's `asyncio`.
- **Raspberry Pi Ready:** Includes a setup script to run as a persistent systemd service.

## 🚀 Quick Start (Local)

1. **Install Dependencies:**
   ```bash
   pip install opencv-python-headless numpy
   ```

2. **Run the Server:**
   ```bash
   python3 server.py
   ```

3. **Connect:**
   In another terminal, run:
   ```bash
   telnet localhost 2772
   # OR
   nc localhost 2772
   ```

## 🍓 Raspberry Pi Deployment

To make your Pi a permanent Matrix host:

1. **Clone & Setup:**
   ```bash
   cd matrix_telnet
   chmod +x setup_pi.sh
   ./setup_pi.sh
   ```
2. **Watch from any device:**
   ```bash
   telnet <your-pi-ip> 2772
   ```

## 🎥 Converting Your Own Videos

You can add any movie scene to the server:

1. **Prepare your video:** Place an `.mp4` file in the project folder.
2. **Convert:**
   ```bash
   python3 converter.py my_scene.mp4 frames/movie_sequence.txt
   ```
3. **Restart the Server:**
   The server automatically detects `frames/movie_sequence.txt` and plays it at high speed.
   ```bash
   sudo systemctl restart matrix-telnet
   ```

## 🛠️ Project Structure

- `server.py`: The heart of the TCP server and sequence controller.
- `matrix_rain.py`: The engine for the digital rain effect.
- `converter.py`: OpenCV script for video-to-ASCII conversion.
- `frames/`:
    - `story.txt`: Static scenes with `=====` delimiters.
    - `movie_sequence.txt`: High-speed frames generated from video.
- `setup_pi.sh`: Automation for systemd service creation.

## 🧼 Terminal Cleanup

If your terminal gets messy or the cursor disappears after a connection, simply run:
```bash
reset
```

---
*Welcome to the desert of the real.*
