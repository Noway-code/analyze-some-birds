from fastapi import FastAPI, File, UploadFile, HTTPException
from analyze.classifier import Classifier
import shutil
import os
import ffmpeg
from fastapi import FastAPI, Request, Depends, Response, status
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
import time
from fastapi.staticfiles import StaticFiles
import logging
import uvicorn
import psutil
import platform
import subprocess

app = FastAPI(title="Bird-Analysis", version="1.0.0")
clf = Classifier()

# only mount videos accesible to frontend
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# Upload is for viewable while validate is for debugging with opencv boxes
UPLOAD_DIR = "videos"
VALIDATE_DIR = "validate"

START_TIME = time.time()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def get_uptime():
    return round(time.time() - START_TIME, 2)


def base_metadata():
    return {
        "service": app.title,
        "version": app.version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": get_uptime(),
    }


def video_validation(file_path):
    try:
        (
            ffmpeg.input(file_path)
            .output("null", f="null")
            .run(capture_stdout=True, capture_stderr=True)
        )
        return True
    except ffmpeg.Error as e:
        logger.warning(
            "Video validation failed", extra={"file": file_path, "error": str(e)}
        )
        return False


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


# Work past memory limit for images, vids, etc. use /temp for working then erase, validate_video will store boxes /validate
@app.post("/validatefile/")
async def create_validate_file(file: UploadFile):
    TEMP_DIR = "./temp/"
    logger.info(file.filename, file.content_type, file.file)
    file_path = os.path.join(TEMP_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    clf.validate_video(file_path)

    logger.info("validation complete, deleting temp file")

    try:
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
        logger.error(f"Additional Details: {repr(e)}")

    return {"filename": file.filename}


# First check if we're fairly confident theres a bird in the video
# If bird, then we'll go ahead and store this for viewing purposes (/videos/bird)
# else it goes to (/videos/other)
@app.post("/uploadfile/", status_code=200)
async def create_upload_file(file: UploadFile):
    logger.info(f"received file {file}, {file.content_type}, {file.file}")
    TEMP_DIR = "./temp/"
    file_path = os.path.join(TEMP_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.exception("Failed to save file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    if not os.path.exists(file_path):
        logger.exception("File was not saved correctly")
        raise HTTPException(status_code=400, detail="File was not saved correctly")

    is_valid = video_validation(file_path)
    if not is_valid:
        os.remove(file_path)
        logger.exception("Uploaded video is corrupted")
        raise HTTPException(status_code=409, detail="Uploaded video is corrupted")

    try:
        is_bird = clf.video_decision(file_path)
    except Exception as e:
        logger.exception("Failed to execute classification, {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to execute classification, {str(e)}"
        )

    final_path = ""

    try:
        if is_bird:
            final_path = os.path.join(UPLOAD_DIR, "bird", file.filename)
            logger.info("bird located")
        else:
            final_path = os.path.join(UPLOAD_DIR, "other", file.filename)
            logger.info("no bird located")
    except Exception as e:
        logger.exception("Detected {is_bird} but join directories failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Detected {is_bird} but join directories failed: {str(e)}",
        )

    try:
        os.rename(file_path, final_path)
    except Exception as e:
        os.remove(file_path)
        logger.exception("Failed to move file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to move file: {str(e)}")
    return {"message": "Success", "path": final_path, "bird": is_bird}


# ==============================
# Website Apis
@app.get("/api/videos")
def list_videos():
    # TODO: Update this to $UPLOAD_DIR once they are available
    files = os.listdir("./videos/bird")
    return [
        {
            "id": f,
            "url": f"/videos/bird/{f}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for f in files
        if f.endswith(".mp4")
    ]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
