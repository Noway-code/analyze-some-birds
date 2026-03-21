from fastapi import FastAPI, File, UploadFile
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

# Work past memory limit for images, vids, etc.
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    print(file.filename, file.content_type, file.file)
    return {"filename": file.filename}
