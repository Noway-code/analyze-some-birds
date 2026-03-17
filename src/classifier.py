from transformers import pipeline
from PIL import Image
import glob
import ffmpeg
import datetime
import os
import math

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
            (
                ffmpeg
                .input(video_path, ss=i) # Seek to the timestamp (ss)
                .output(output_path, vframes=1) # Output only one frame (vframes=1)
                .run(overwrite_output=True, quiet=True)
            )
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
    sample_frames(idx,vid)
    idx+=1
 #   with Image.open(image) as img:
 #       print(classifier(img))



