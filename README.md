# AI DJ Assistant

A full-stack web app that analyzes DJ tracks and builds harmonically mixed sets, then exports them straight into Rekordbox.

Built as a DJ (hard techno / schranz) who wanted to automate the mix prep I already do by ear, across a whole track library instead of one pair at a time.

## What it does

- **Analyzes tracks** — BPM, musical key, energy, and danceability, using real audio signal processing (librosa + Essentia), not estimates
- **Batch folder analysis** — upload a whole library at once, not one track at a time
- **Harmonic mixing engine** — converts keys to Camelot wheel notation and finds compatible transitions (±1, ±2, and relative major/minor)
- **Bridge track finder** — suggests a track to play in between two otherwise-incompatible keys
- **Set builder** — generates a full ordered set (opening / peak time / closing) using a sequencing algorithm that respects tempo range and shapes the energy arc across the set
- **Rekordbox export** — generates a real Rekordbox XML playlist, ready to import and mix
- **Relative star ratings** — energy, danceability, and key confidence scored 1–5 against your own library's actual range, not arbitrary fixed thresholds



## Stack

**Backend:** Python, FastAPI, librosa, Essentia, SQLite **Frontend:** React, Vite **Export:** Rekordbox XML

## Why I built it this way

This was my first backend and full-stack project — first time touching a terminal, Git, or writing an API. A few real problems I had to work through along the way:

- The initial set-building algorithm was a greedy nearest-match approach that worked well most of the time, but clustered tempo outliers at the very end of a generated set. Fixed by filtering candidate tracks by tempo range per context, and adding a moving energy ceiling/floor for opening and closing sets instead of a flat scoring bonus.
- Key detection confidence varies meaningfully by genre — tracks with thin harmonic content (e.g. stripped-back techno) get lower-confidence key reads than melodic or vocal-driven tracks, which the app now surfaces as a rating rather than hiding.
- Essentia's raw danceability output isn't a 0–100% scale — it needed to be rescaled relative to the actual library before it meant anything to a person looking at it.



## Running it locally

```bash
# backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install librosa essentia fastapi uvicorn python-multipart
uvicorn main:app --reload

# frontend (new terminal)
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`.

## Status

Actively working on this — multi-user support and a hosted version are potential next steps. Open to feedback from other DJs or developers.

