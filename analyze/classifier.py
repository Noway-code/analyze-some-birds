from transformers import pipeline
from fastapi import HTTPException
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

    def __init__(self, confidence=0.40, hit_threshold=20):
        print("classifier initialized")
        self.model = YOLO("yolov8n.pt")
        self.confidence = confidence
        self.hit_threshold = hit_threshold

    def run_video(self, vid: str):
        self.validate_video(vid)

    def run_directory(self, directory_path: str):
        for vid in glob.glob(os.path.join(directory_path, "*.mp4")):
            self.validate_video(vid)

    def get_resolution(self, cap):
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        return w, h, fps

    def validate_video(self, video_path: str):
        cap = cv2.VideoCapture(video_path)
        output_path = "validate"

        out_path = os.path.join(output_path, os.path.basename(video_path))

        w, h, fps = self.get_resolution(cap)
        writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

        results = self.model.track(
            source=video_path,
            stream=True,
            persist=True,
            classes=[14],  # COCO class: bird
            conf=self.confidence,
        )

        for result in results:
            if result.boxes is None:
                continue

            annotated = result.plot()
            writer.write(annotated)

        cap.release()
        writer.release()

    def video_decision(self, video_path: str):
        threshold = self.hit_threshold
        try:
            raise Exception("just testing failure")
            results = self.model.track(
                source=video_path,
                stream=True,
                persist=False,
                classes=[14],  # COCO class: bird
                conf=self.confidence,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to track with YOLO: {str(e)}",
            )

        hits = 0
        frame = 0
        for result in results:
            frame += 1
            if result.boxes is not None and len(result.boxes) > 0:
                hits += 1
                print(" Hit!")
                if hits >= threshold:
                    return True
            else:
                print(f"Currently at {hits}/{frame}")

        return False
