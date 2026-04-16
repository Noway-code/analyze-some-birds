from fastapi import FastAPI, File, UploadFile
from analyze.classifier import Classifier
import shutil
import os
from fastapi import FastAPI, Request, Depends, Response, status
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
import time
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Bird-Analysis", version="1.0.0")
clf = Classifier()

# only mount videos accesible to frontend
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# Upload is for viewable while validate is for debugging with opencv boxes
UPLOAD_DIR = "videos"
VALIDATE_DIR = "validate"

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


# Work past memory limit for images, vids, etc. use /temp for working then erase, validate_video will store boxes /validate
@app.post("/validatefile/")
async def create_validate_file(file: UploadFile):
    TEMP_DIR = "./temp/"
    print(file.filename, file.content_type, file.file)
    file_path = os.path.join(TEMP_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    clf.validate_video(file_path)

    print("validation complete, deleting temp file")

    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Failed to delete file: {str(e)}")
        print(f"Additional Details: {repr(e)}")

    return {"filename": file.filename}


# First check if we're fairly confident theres a bird in the video
# If bird, then we'll go ahead and store this for viewing purposes (/videos/bird)
# else it goes to (/videos/other)
@app.post("/uploadfile/", status_code=200)
async def create_upload_file(file: UploadFile, response: Response):
    print(f"received file {file}, {file.content_type}, {file.file}")
    TEMP_DIR = "./temp/"
    file_path = os.path.join(TEMP_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if not os.path.exists(file_path):
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    is_bird = clf.video_decision(file_path)
    final_path = ""
    if is_bird:
        final_path = os.path.join(UPLOAD_DIR, "bird", file.filename)
        print("bird located")
    else:
        final_path = os.path.join(UPLOAD_DIR, "other", file.filename)
        print("no bird located")

    os.rename(file_path, final_path)
    return f"New Location: {final_path}"


@app.get("/api/videos")
def list_videos():
    # TODO: Update this to $UPLOAD_DIR once they are available
    files = os.listdir("./data")
    return [
        {
            "id": f,
            "url": f"/videos/{f}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for f in files
        if f.endswith(".mp4")
    ]
