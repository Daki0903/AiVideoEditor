import librosa
import numpy as np

def analyze_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
    times = librosa.frames_to_time(peaks, sr=sr)
    return times
