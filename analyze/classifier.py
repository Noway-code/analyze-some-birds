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
from fastapi import UploadFile


class Classifier:
    def __init__(self):
        print("classifier initialized")
        self.output_path = 'validate'
        self.model = YOLO("yolov8n.pt") 

    def run_video(self,vid:str):
            self.yolo(vid)
    def run_directory(self, directory_path: str):
        for vid in glob.glob(os.path.join(directory_path, "*.mp4")):
            self.yolo(vid)

    def get_resolution(self,cap):
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        return w, h, fps

    def yolo(self, video_path:str):
        cap = cv2.VideoCapture(video_path)

        out_path = os.path.join(self.output_path, os.path.basename(video_path))

        w,h,fps = self.get_resolution(cap)
        writer = cv2.VideoWriter(
            out_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (w, h)
        )

        results = self.model.track(
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

        



