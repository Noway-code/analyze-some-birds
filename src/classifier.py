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
import json


def get_resolution(video_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "json", video_path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    w = data["streams"][0]["width"]
    h = data["streams"][0]["height"]
    return w, h

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
    width, height = get_resolution(video_path) 
    frame_size = width * height * 3
    i = 0
    success=0
    total=0
    print(f"running {video_path}")
    while True:
        raw = process.stdout.read(frame_size)
        if len(raw) != frame_size:
            break

        frame = np.frombuffer(raw, np.uint8).reshape((height, width, 3))
        pil_image = Image.fromarray(frame)
        result = classifier(pil_image)
        
        candidate = result[0]
        label = candidate['label']
        score = candidate['score']
        
        if label != "NORTHERN CARDINAL" or score < .50:
            output_path = os.path.join("validate", f"{label}-{score}__{time.time()}.jpg")
            pil_image.save(output_path)
        else:
            success+=1
        total+=1

    print(f"{success}, {total}, accuracy: {success/total}")
    process.stdout.close()
    process.stderr.close()
    process.wait()

classifier = pipeline(
    "image-classification",
    model="chriamue/bird-species-classifier"
)
directory_path = 'data/*.mp4'
for vid in glob.glob(directory_path):
    subprocess_frames(vid)
    



