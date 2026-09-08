import sqlite3
from camelot import get_camelot

DB_PATH = "tracks.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            bpm REAL,
            key TEXT,
            key_confidence REAL,
            energy REAL,
            danceability REAL
        )
    """)
    conn.commit()
    conn.close()

def save_track(filename, bpm, key, key_confidence, energy, danceability):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tracks (filename, bpm, key, key_confidence, energy, danceability)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (filename, bpm, key, key_confidence, energy, danceability))
    conn.commit()
    track_id = cursor.lastrowid
    conn.close()
    return track_id

def _scale_to_rating(value, min_val, max_val):
    """Map a raw value onto a 1-5 rating based on the real min/max in the library."""
    if max_val == min_val:
        return 3  # no variance to compare against, default to a neutral middle rating
    scaled = (value - min_val) / (max_val - min_val)
    rating = 1 + scaled * 4
    return max(1, min(5, round(rating)))

def get_all_tracks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks")
    rows = cursor.fetchall()
    conn.close()

    tracks = []
    for row in rows:
        track = dict(row)
        key_parts = track["key"].split(" ", 1)
        track["camelot"] = get_camelot(key_parts[0], key_parts[1])
        tracks.append(track)

    if len(tracks) == 0:
        return tracks

    energies = [t["energy"] for t in tracks]
    danceabilities = [t["danceability"] for t in tracks]
    min_e, max_e = min(energies), max(energies)
    min_d, max_d = min(danceabilities), max(danceabilities)

    for t in tracks:
        t["energy_rating"] = _scale_to_rating(t["energy"], min_e, max_e)
        t["danceability_rating"] = _scale_to_rating(t["danceability"], min_d, max_d)
        t["key_confidence_rating"] = max(1, min(5, round(t["key_confidence"] * 5)))

    return tracks