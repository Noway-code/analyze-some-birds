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
from ultralytics import YOLO
import pprint
directory_path = 'data/*.mp4'
output_path = 'validate'
model = YOLO("yolov8n.pt") 


def get_resolution(cap):
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return w, h, fps

def yolo(video_path):
    cap = cv2.VideoCapture(video_path)
    out_path = os.path.join(output_path, os.path.basename(video_path))
    w,h,fps = get_resolution(cap)
    writer = cv2.VideoWriter(
        out_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    results = model.track(
        source=video_path,
        stream=True,
        persist=True,
        classes=[14],  # COCO class: bird
        conf=0.30
    )

    for result in results:
        if result.boxes is None:
            continue

        annotated = result.plot()
        writer.write(annotated)

    cap.release()
    writer.release()

for vid in glob.glob(directory_path):
    yolo(vid)
    



