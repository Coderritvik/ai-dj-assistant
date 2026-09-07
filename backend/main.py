from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from analyze import analyze_track
from database import init_db, save_track, get_all_tracks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = analyze_track(temp_path)
    finally:
        os.remove(temp_path)

    track_id = save_track(
        filename=file.filename,
        bpm=result["bpm"],
        key=result["key"],
        key_confidence=result["key_confidence"],
        energy=result["energy"],
        danceability=result["danceability"]
    )

    result["id"] = track_id
    return result


@app.get("/tracks")
async def list_tracks():
    return get_all_tracks()