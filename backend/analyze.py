import librosa
import essentia
import essentia.standard as es

filepath = "test_audio/Katy Perry - Dark Horse ft. Juicy J (AANSE Remix) - West Coast Residency Edits, AANSE - SoundLoadMate.com.mp3"

# BPM detection using librosa
y, sr = librosa.load(filepath)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

# Key detection using essentia
loader = es.MonoLoader(filename=filepath)
audio = loader()
key_extractor = es.KeyExtractor()
key, scale, strength = key_extractor(audio)

print(f"Estimated BPM: {tempo[0]:.1f}")
print(f"Estimated Key: {key} {scale}")
print(f"Key confidence: {strength:.2f}")