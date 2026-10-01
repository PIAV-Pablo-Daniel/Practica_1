import cv2

def write_video(path, frames, fps=6, repeats=4):
    """
    Exporta una lista de fotogramas (BGR) a un archivo de vídeo MP4 paso a paso.
    Cada fotograma se repite para poder visualizar la secuencia con claridad.
    """
    if not frames:
        return False
    h, w = frames[0].shape[:2]
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    if not writer.isOpened():
        return False
    for frame in frames:
        for _ in range(repeats):
            writer.write(frame)
    writer.release()
    return True