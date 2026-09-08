from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
from analyze import analyze_track
from database import init_db, save_track, get_all_tracks
from camelot import get_camelot, is_harmonically_compatible
from set_builder import build_set
from fastapi.responses import FileResponse
from rekordbox_export import generate_rekordbox_xml, save_xml

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

    all_tracks = get_all_tracks()
    saved_track = next(t for t in all_tracks if t["id"] == track_id)
    return saved_track


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


@app.get("/bridge")
async def find_bridge(from_track_id: int, to_track_id: int):
    all_tracks = get_all_tracks()

    from_track = next((t for t in all_tracks if t["id"] == from_track_id), None)
    to_track = next((t for t in all_tracks if t["id"] == to_track_id), None)

    if from_track is None or to_track is None:
        return {"error": "One or both tracks not found"}

    from_key_parts = from_track["key"].split(" ", 1)
    to_key_parts = to_track["key"].split(" ", 1)
    from_camelot = get_camelot(from_key_parts[0], from_key_parts[1])
    to_camelot = get_camelot(to_key_parts[0], to_key_parts[1])

    if is_harmonically_compatible(from_camelot, to_camelot):
        return {
            "bridge_needed": False,
            "message": "These tracks are already harmonically compatible"
        }

    candidates = []
    for track in all_tracks:
        if track["id"] in (from_track_id, to_track_id):
            continue

        key_parts = track["key"].split(" ", 1)
        track_camelot = get_camelot(key_parts[0], key_parts[1])

        compatible_with_from = is_harmonically_compatible(from_camelot, track_camelot)
        compatible_with_to = is_harmonically_compatible(track_camelot, to_camelot)

        if compatible_with_from and compatible_with_to:
            bpm_diff_from = abs(track["bpm"] - from_track["bpm"])
            bpm_diff_to = abs(track["bpm"] - to_track["bpm"])
            candidates.append({
                **track,
                "camelot": track_camelot,
                "total_bpm_diff": round(bpm_diff_from + bpm_diff_to, 1)
            })

    candidates.sort(key=lambda t: t["total_bpm_diff"])

    return {
        "bridge_needed": True,
        "from_track": from_track["filename"],
        "from_camelot": from_camelot,
        "to_track": to_track["filename"],
        "to_camelot": to_camelot,
        "bridge_candidates": candidates
    }

@app.get("/export-set")
async def export_set(context: str = "peak", count: int = None):
    all_tracks = get_all_tracks()

    if context not in ["opening", "peak", "closing"]:
        return {"error": "context must be 'opening', 'peak', or 'closing'"}

    ordered = build_set(all_tracks, context)

    if count is not None:
        ordered = ordered[:count]

    if len(ordered) == 0:
        return {"error": "No tracks available for this set"}

    playlist_name = f"{context.capitalize()} Set"
    xml_root = generate_rekordbox_xml(ordered, playlist_name)

    output_path = "rekordbox_export.xml"
    save_xml(xml_root, output_path)

    return FileResponse(
        output_path,
        media_type="application/xml",
        filename="rekordbox_export.xml"
    )