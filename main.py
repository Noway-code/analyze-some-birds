from fastapi import FastAPI, File, UploadFile
from analyze.classifier import Classifier
import shutil
import os
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
import time
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Bird-Analysis", version="1.0.0")
clf = Classifier()
app.mount("/videos", StaticFiles(directory="videos"), name="videos")
app.mount("/validate", StaticFiles(directory="validate"), name="validate")

UPLOAD_DIR = "validate"

START_TIME = time.time()


def get_uptime():
    return round(time.time() - START_TIME, 2)


def base_metadata():
    return {
        "service": app.title,
        "version": app.version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": get_uptime(),
    }


@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}


@app.get("/health", tags=["health"])
async def health():
    """
    Lightweight liveness probe.
    Should be fast and not depend on external systems.
    """
    return {"status": "ok", **base_metadata()}


# Work past memory limit for images, vids, etc.
@app.post("/validatefile/")
async def create_validate_file(file: UploadFile):
    print(file.filename, file.content_type, file.file)
    file_path = os.path.join(VALIDATE_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    clf.validate_video(file_path)

    return {"filename": file.filename}


# First check if we're fairly confident theres a bird in the video
# If bird, then we'll go ahead and store this for viewing purposes (/videos/bird)
# else it goes to (/videos/other)
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    print(f"received file {file}, {file.content_type}, {file.file}")
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    clf.validate_video(file_path)

    return {"filename": file.filename}


@app.get("/api/videos")
def list_videos():
    files = os.listdir(UPLOAD_DIR)
    return [
        {
            "id": f,
            "url": f"/videos/{f}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for f in files
        if f.endswith(".mp4")
    ]
