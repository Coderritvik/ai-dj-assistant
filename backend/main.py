from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
from analyze import analyze_track
from database import init_db, save_track, get_all_tracks
from camelot import get_camelot, is_harmonically_compatible
from set_builder import build_set

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

LIBRARY_DIR = "library"
os.makedirs(LIBRARY_DIR, exist_ok=True)


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


@app.post("/analyze-folder")
async def analyze_folder(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        permanent_path = os.path.join(LIBRARY_DIR, file.filename)
        with open(permanent_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            result = analyze_track(permanent_path)
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
            continue

        track_id = save_track(
            filename=file.filename,
            bpm=result["bpm"],
            key=result["key"],
            key_confidence=result["key_confidence"],
            energy=result["energy"],
            danceability=result["danceability"]
        )

        result["id"] = track_id
        result["filename"] = file.filename
        results.append(result)

    return {"analyzed": results}


@app.get("/tracks")
async def list_tracks():
    return get_all_tracks()


@app.get("/recommendations/{track_id}")
async def get_recommendations(track_id: int):
    all_tracks = get_all_tracks()

    target = None
    for track in all_tracks:
        if track["id"] == track_id:
            target = track
            break

    if target is None:
        return {"error": "Track not found"}

    target_key_parts = target["key"].split(" ", 1)
    target_camelot = get_camelot(target_key_parts[0], target_key_parts[1])

    scored_matches = []
    for track in all_tracks:
        if track["id"] == track_id:
            continue

        key_parts = track["key"].split(" ", 1)
        track_camelot = get_camelot(key_parts[0], key_parts[1])

        bpm_diff = abs(track["bpm"] - target["bpm"])
        harmonic_match = is_harmonically_compatible(target_camelot, track_camelot)

        score = 0
        if harmonic_match:
            score += 100
        score -= bpm_diff

        scored_matches.append({
            **track,
            "camelot": track_camelot,
            "harmonic_match": harmonic_match,
            "bpm_diff": round(bpm_diff, 1),
            "score": round(score, 1)
        })

    scored_matches.sort(key=lambda x: x["score"], reverse=True)

    return {
        "target_track": target["filename"],
        "target_camelot": target_camelot,
        "recommendations": scored_matches
    }

@app.get("/generate-set")
async def generate_set(context: str = "peak", count: int = None):
    all_tracks = get_all_tracks()

    if context not in ["opening", "peak", "closing"]:
        return {"error": "context must be 'opening', 'peak', or 'closing'"}

    ordered = build_set(all_tracks, context)

    if count is not None:
        ordered = ordered[:count]

    return {
        "context": context,
        "track_count": len(ordered),
        "set": ordered
    }