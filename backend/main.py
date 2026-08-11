from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from analyze import analyze_track

app = FastAPI()

# This allows your future React frontend (running on a different port)
# to actually talk to this backend. Without this, browsers block the request.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # Save the uploaded file temporarily so librosa/essentia can read it from disk
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = analyze_track(temp_path)
    finally:
        # Clean up the temp file whether analysis succeeded or failed
        os.remove(temp_path)

    return result