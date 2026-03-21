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
model = YOLO("yolov8s.pt")  # use yolov8s.pt if you want better accuracy

#classifier = pipeline("image-classification", model="dennisjooo/Birds-Classifier-EfficientNetB2")

def get_resolution(cap):
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return w, h, fps

#def subprocess_frames(video_path):
#    process = subprocess.Popen(
#    [
#        "ffmpeg",
#        "-i", video_path,
#        "-f", "image2pipe",
#        "-pix_fmt", "rgb24",
#        "-vcodec", "rawvideo",
#        "-"
#    ],
#    stdout=subprocess.PIPE,
#    stderr=subprocess.PIPE
#    )
#    width, height, _= get_resolution(video_path) 
#    frame_size = width * height * 3
#    i = 0
#    success=0
#    total=0
#    print(f"running {video_path}")
#    while True:
#        raw = process.stdout.read(frame_size)
#        if len(raw) != frame_size:
#            break
#
#        frame = np.frombuffer(raw, np.uint8).reshape((height, width, 3))
#        pil_image = Image.fromarray(frame)
#        result = classifier(pil_image)
#        
#        candidate = result[0]
#        label = candidate['label']
#        score = candidate['score']
#        
#        total+=1
#
#    print(f"{success}, {total}, accuracy: {success/total}")
#    process.stdout.close()
#    process.stderr.close()
#    process.wait()
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

    for frame in results:
        frame_img = frame.orig_img 
        boxes = frame.boxes

        # Check if anything was identified before tensors ops
        if boxes is None:
            continue
        
        # Convert box tensors from hgface to actual numpy coords
        boxes = frame.boxes.xyxy.cpu().numpy()
        ids = frame.boxes.id

        if ids is not None:
            ids = ids.numpy()

        # There can be multiple boxes i.e birds
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)

            track_id = int(ids[i]) 

            cv2.rectangle(frame_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame_img,
                f"bird {track_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        writer.write(frame_img)

    cap.release()
    writer.release()


for vid in glob.glob(directory_path):
    yolo(vid)
    



