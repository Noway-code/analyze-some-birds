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
import cv2


def get_resolution(video_path):
    cap = cv2.VideoCapture(video_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return w, h, fps

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
    width, height, _= get_resolution(video_path) 
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
        
        if score < .50:
            output_path = os.path.join("validate", f"{label}-{score}__{time.time()}.jpg")
            pil_image.save(output_path)
        else:
            success+=1
        total+=1

    print(f"{success}, {total}, accuracy: {success/total}")
    process.stdout.close()
    process.stderr.close()
    process.wait()

classifier = pipeline("image-classification", model="dennisjooo/Birds-Classifier-EfficientNetB2")
directory_path = 'data/*.mp4'
for vid in glob.glob(directory_path):
    subprocess_frames(vid)
    



