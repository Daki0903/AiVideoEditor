import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

def generate_highlights(video_path, highlight_times, output_path="output/highlight.mp4", segment_length=5, bitrate="3000k", preset="medium"):
    clip = VideoFileClip(video_path)
    clips = []

    for t in highlight_times:
        start = max(t - 2, 0)
        end = min(t + segment_length, clip.duration)
        clips.append(clip.subclip(start, end))

    final_clip = concatenate_videoclips(clips)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_clip.write_videofile(output_path, bitrate=bitrate, preset=preset)
