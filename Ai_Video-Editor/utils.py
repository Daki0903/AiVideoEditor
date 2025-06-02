import cv2
import librosa
from moviepy.editor import VideoFileClip, concatenate_videoclips
import numpy as np

def analyze_audio(path):
    y, sr = librosa.load(path)
    hop_length = 512
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr, hop_length=hop_length)
    peaks = librosa.util.peak_pick(onset_env, 3,3,3,5,0.5,10)
    return times[peaks]

def analyze_video_motion(path, threshold=30):
    cap = cv2.VideoCapture(path)
    ret, prev_frame = cap.read()
    if not ret:
        return []

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    motion_times = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, prev_gray)
        non_zero_count = np.sum(diff > threshold)
        if non_zero_count > 50000:  # prilagodi po potrebi
            motion_times.append(frame_number / fps)
        prev_gray = gray
        frame_number += 1

    cap.release()
    # Smanji duplikate oko istog trenutka
    filtered = []
    for t in motion_times:
        if not filtered or t - filtered[-1] > 1:
            filtered.append(t)
    return filtered

def combine_times(audio_times, motion_times):
    combined = list(set(audio_times) | set(motion_times))
    combined.sort()
    return combined

def generate_highlights(video_path, times, output_path="output/highlight.mp4", segment_duration=5, bitrate="3000k", preset="medium"):
    clip = VideoFileClip(video_path)
    clips = []
    for t in times:
        start = max(t - 2, 0)
        end = min(t + segment_duration, clip.duration)
        subclip = clip.subclip(start, end)
        clips.append(subclip)
    final = concatenate_videoclips(clips)
    final.write_videofile(output_path, bitrate=bitrate, preset=preset)
