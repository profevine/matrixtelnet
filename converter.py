import cv2
import numpy as np
import sys
import os

# ASCII characters from light to dark (optimized for dark terminals)
# Space for black, dense characters for white
ASCII_CHARS = " .:-=+*#%@"

def frame_to_ascii(frame, width=80):
    height, original_width = frame.shape[:2]
    aspect_ratio = height / original_width
    new_height = int(width * aspect_ratio * 0.5)
    
    resized_frame = cv2.resize(frame, (width, new_height))
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    
    # Improve contrast using Histogram Equalization
    gray_frame = cv2.equalizeHist(gray_frame)
    
    pixels = gray_frame.flatten()
    # Map pixels to characters: 0 (black) -> " ", 255 (white) -> "@"
    chars = [ASCII_CHARS[pixel * (len(ASCII_CHARS) - 1) // 255] for pixel in pixels]
    
    ascii_str = "".join(chars)
    frame_ascii = "\n".join([ascii_str[i:(i + width)] for i in range(0, len(ascii_str), width)])
    return frame_ascii

def convert_video(input_path, output_path, width=80, max_frames=1000):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_path}")
        return

    frames_count = 0
    with open(output_path, 'w') as f:
        while True:
            ret, frame = cap.read()
            if not ret or frames_count >= max_frames:
                break
            
            ascii_frame = frame_to_ascii(frame, width)
            f.write("=====\n")
            f.write(ascii_frame + "\n")
            
            frames_count += 1
            if frames_count % 10 == 0:
                print(f"Converted {frames_count} frames...", end='\r')
                
    cap.release()
    print(f"\nDone! Converted {frames_count} frames to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 converter.py input_video.mp4 [output_file.txt]")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "frames/movie_sequence.txt"
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        convert_video(input_file, output_file)
