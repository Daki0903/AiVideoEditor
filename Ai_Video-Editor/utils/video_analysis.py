import cv2
import numpy as np

def detect_motion(video_path, threshold=30, min_area=50000):
    cap = cv2.VideoCapture(video_path)
    ret, prev_frame = cap.read()
    if not ret:
        return []

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    motion_times = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, prev_gray)
        count = np.sum(diff > threshold)

        if count > min_area:
            motion_times.append(frame_count / fps)

        prev_gray = gray
        frame_count += 1

    cap.release()

    # filtriraj bliske trenutke
    filtered = []
    for t in motion_times:
        if not filtered or t - filtered[-1] > 1.0:
            filtered.append(t)
    return filtered
