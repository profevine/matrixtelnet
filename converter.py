import cv2
import numpy as np
import sys
import os

# Refined ASCII map for better gradients (light to dark for black background)
# Using more characters for smoother transitions
ASCII_CHARS = " .':,;+*#%S$X@ "

def frame_to_ascii(frame, width=80):
    # 1. Resize while maintaining aspect ratio
    height, original_width = frame.shape[:2]
    aspect_ratio = height / original_width
    new_height = int(width * aspect_ratio * 0.5)
    resized_frame = cv2.resize(frame, (width, new_height))
    
    # 2. Grayscale
    gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    
    # 3. Enhance Contrast (CLAHE - Contrast Limited Adaptive Histogram Equalization)
    # This is much better than simple equalization for movies with dark and light areas
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # 4. Brightness Boost (Optional: shift values up slightly)
    # alpha=1.2 (contrast boost), beta=20 (brightness boost)
    enhanced = cv2.convertScaleAbs(enhanced, alpha=1.1, beta=10)
    
    # 5. Map pixels to characters
    # Map 0-255 to 0-(len-1)
    pixels = enhanced.flatten()
    num_chars = len(ASCII_CHARS)
    chars = [ASCII_CHARS[int(p * (num_chars - 1) / 255)] for p in pixels]
    
    ascii_str = "".join(chars)
    frame_ascii = "\n".join([ascii_str[i:(i + width)] for i in range(0, len(ascii_str), width)])
    return frame_ascii

def convert_video(input_path, output_path, width=80, max_frames=None):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_path}")
        return

    frames_count = 0
    print(f"Starting conversion of {input_path}...")
    
    with open(output_path, 'w') as f:
        while True:
            ret, frame = cap.read()
            if not ret or (max_frames is not None and frames_count >= max_frames):
                break
            
            ascii_frame = frame_to_ascii(frame, width)
            f.write("=====\n")
            f.write(ascii_frame + "\n")
            
            frames_count += 1
            if frames_count % 30 == 0:
                print(f"Converted {frames_count} frames...", end='\r')
                
    cap.release()
    print(f"\nDone! Converted {frames_count} frames to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 converter.py input_video.mp4 [output_file.txt] [width]")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "frames/movie_sequence.txt"
        width_arg = int(sys.argv[3]) if len(sys.argv) > 3 else 80
        
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        convert_video(input_file, output_file, width=width_arg)
