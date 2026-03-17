from transformers import pipeline
from PIL import Image
import glob
import ffmpeg
import datetime
import os
import math
import subprocess
import numpy as np
import time

width = 1280
height = 720
def subprocess_frames(video_path):
    process = subprocess.Popen(
    [
        "ffmpeg",
        "-i", video_path,
        "-f", "image2pipe",
        "-pix_fmt", "rgb24",
        "-vcodec", "rawvideo",
        "-"
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
    )
    
    frame_size = width * height * 3
    i = 0
    while True:
        raw = process.stdout.read(frame_size)
        if len(raw) != frame_size:
            break

        frame = np.frombuffer(raw, np.uint8).reshape((height, width, 3))
        pil_image = Image.fromarray(frame)
        result = classifier(pil_image)
        
        print(result[0]['score'])
        output_path = os.path.join("validate", f"{time.time()}_{i}.jpg")
        pil_image.save(output_path)

def sample_frames(idx,video_path, output_folder="out"):
    """
    Extracts frames at specific timestamps (in seconds) using ffmpeg-python.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    metadata = ffmpeg.probe(video_path) 
    duration_seconds = math.floor(float(metadata["format"]["duration"]))
    print(f"Going for {duration_seconds}")
    for i in range(duration_seconds):
        output_path = os.path.join(output_folder, f"vid_{idx}_frame_at_{i}s_{i}.jpg")
        try:
            ffmpeg.input(video_path, ss=i).output(output_path, vframes=1).run(overwrite_output=True, quiet=True)
            print(f"Saved frame at {i}s to {output_path}")
        except Exception as e:
            print("welp", e)

classifier = pipeline(
    "image-classification",
    model="chriamue/bird-species-classifier"
)
directory_path = 'data/*.mp4'
idx = 0
for vid in glob.glob(directory_path):
    subprocess_frames(vid)
    



