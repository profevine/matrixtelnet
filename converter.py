"""
DISCLAIMER: This project is for educational purposes only and has no commercial intent.
"The Matrix" is a registered trademark of Warner Bros. Entertainment Inc.
"""

import cv2
import numpy as np
import sys
import os

ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def get_ansi_color(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def frame_to_colored_ascii(frame, width=80):
    height, original_width = frame.shape[:2]
    aspect_ratio = height / original_width
    new_height = int(width * aspect_ratio * 0.5)

    resized_frame = cv2.resize(frame, (width, new_height))
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

    ascii_rows = []
    last_color = ""
    reset = "\033[0m"

    for y in range(new_height):
        row_str = ""
        for x in range(width):
            pixel_gray = gray_frame[y, x]
            pixel_bgr = resized_frame[y, x]
            r, g, b = pixel_bgr[2], pixel_bgr[1], pixel_bgr[0]

            char = ASCII_CHARS[int(pixel_gray * (len(ASCII_CHARS) - 1) / 255)]
            color = get_ansi_color(r, g, b)

            if color != last_color:
                row_str += color
                last_color = color

            row_str += char

        ascii_rows.append(row_str + reset)
        last_color = ""

    return "\n".join(ascii_rows)

def convert_video(input_path, output_path, width=80, max_frames=None):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_path}")
        return

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if max_frames is not None:
        total = min(total, max_frames)

    print(f"Converting {input_path}  ({total} frames, width={width})...")

    frames_count = 0
    with open(output_path, 'w') as f:
        while True:
            ret, frame = cap.read()
            if not ret or (max_frames is not None and frames_count >= max_frames):
                break

            ascii_frame = frame_to_colored_ascii(frame, width)
            f.write("=====\n")
            f.write(ascii_frame + "\n")

            frames_count += 1
            if frames_count % 10 == 0:
                pct = frames_count / total * 100 if total > 0 else 0
                print(f"  {frames_count}/{total} frames  ({pct:.1f}%)", end='\r')

    cap.release()
    print(f"\nDone! {frames_count} frames → {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 converter.py input_video.mp4 [output_file.txt] [width]")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "frames/movie_sequence.txt"
        width_arg = int(sys.argv[3]) if len(sys.argv) > 3 else 80

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        convert_video(input_file, output_file, width=width_arg)
