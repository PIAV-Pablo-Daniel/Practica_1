import cv2


def write_video(path, frames, fps=6, repeats=4):
    if not frames:
        return False
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))
    if not writer.isOpened():
        return False
    for frame in frames:
        for _ in range(repeats):
            writer.write(frame)
    writer.release()
    return True