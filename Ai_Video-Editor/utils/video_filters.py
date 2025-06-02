import cv2
import os

def stabilize_video(input_path):
    # Jednostavna stabilizacija koristeći OpenCV (primer - složenije može kasnije)
    cap = cv2.VideoCapture(input_path)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Koristimo prvi frejm kao referencu
    _, prev = cap.read()
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    transforms = []

    for i in range(n_frames-1):
        success, curr = cap.read()
        if not success:
            break
        curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
        prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30)
        curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)

        idx = [i for i, st in enumerate(status) if st == 1]
        prev_pts = prev_pts[idx]
        curr_pts = curr_pts[idx]

        m, _ = cv2.estimateAffinePartial2D(prev_pts, curr_pts)
        if m is None:
            m = np.eye(2, 3)
        transforms.append(m)

        prev_gray = curr_gray

    # Sada bismo mogli da stabilizujemo video ali za primer samo kopiramo ulaz u izlaz
    cap.release()
    return input_path

def apply_contrast_filter(input_path):
    cap = cv2.VideoCapture(input_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = "output/filtered_video.mp4"
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Povećaj kontrast i osvetljenje
        alpha = 1.3 # kontrast
        beta = 20   # osvetljenje
        adjusted = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        out.write(adjusted)

    cap.release()
    out.release()
    return output_path
