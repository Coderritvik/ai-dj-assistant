import sqlite3

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

def get_all_tracks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]