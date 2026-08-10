import librosa
import essentia
import essentia.standard as es

def analyze_track(filepath):
    # BPM detection using librosa
    y, sr = librosa.load(filepath)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # Key detection using essentia
    loader = es.MonoLoader(filename=filepath)
    audio = loader()
    key_extractor = es.KeyExtractor()
    key, scale, strength = key_extractor(audio)

    # Energy estimation using essentia
    rms = es.RMS()
    energy_value = rms(audio)

    # Danceability estimation using essentia
    danceability_extractor = es.Danceability()
    danceability_value, dfa_curve = danceability_extractor(audio)

    return {
        "bpm": round(float(tempo[0]), 1),
        "key": f"{key} {scale}",
        "key_confidence": round(float(strength), 2),
        "energy": round(float(energy_value), 4),
        "danceability": round(float(danceability_value), 4)
    }


# This block only runs when you execute this file directly
# (not when another file imports analyze_track from it)
if __name__ == "__main__":
    filepath = "test_audio/Katy Perry - Dark Horse ft. Juicy J (AANSE Remix) - West Coast Residency Edits, AANSE - SoundLoadMate.com.mp3"
    result = analyze_track(filepath)
    print(result)