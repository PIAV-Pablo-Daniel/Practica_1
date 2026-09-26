import cv2

def write_video(path, frames, fps=6, repeats=4):
    """
    Exporta una lista de fotogramas (imágenes en formato BGR) a un archivo de vídeo MP4.
    Cada fotograma se repite para permitir observar el proceso paso a paso con claridad.
    """
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