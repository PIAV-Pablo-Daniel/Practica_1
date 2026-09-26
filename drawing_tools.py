import cv2
import numpy as np

def draw_line(img, p1, p2, color, thickness):
    """Dibuja una línea entre p1 y p2 con antialiasing."""
    cv2.line(img, p1, p2, color, thickness, lineType=cv2.LINE_AA)

def draw_rectangle(img, p1, p2, color, thickness):
    """Dibuja un rectángulo normalizando las esquinas para admitir cualquier cuadrante de arrastre."""
    pt1 = (min(p1[0], p2[0]), min(p1[1], p2[1]))
    pt2 = (max(p1[0], p2[0]), max(p1[1], p2[1]))
    cv2.rectangle(img, pt1, pt2, color, thickness)

def draw_circle(img, p1, p2, color, thickness):
    """Dibuja un círculo con centro en p1 y radio igual a la distancia euclídea hasta p2."""
    radius = int(((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5)
    cv2.circle(img, p1, radius, color, thickness, lineType=cv2.LINE_AA)

def draw_ellipse(img, p1, p2, color, thickness):
    """Dibuja una elipse inscrita en la caja delimitadora definida por p1 y p2."""
    center = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
    axes = (max(1, abs(p2[0] - p1[0]) // 2), max(1, abs(p2[1] - p1[1]) // 2))
    cv2.ellipse(img, center, axes, 0, 0, 360, color, thickness, lineType=cv2.LINE_AA)

def draw_polyline(img, points, color, thickness):
    """Dibuja una secuencia de segmentos conectados (abierta)."""
    if len(points) >= 2:
        pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(img, [pts], isClosed=False, color=color, thickness=thickness, lineType=cv2.LINE_AA)

def draw_polygon(img, points, color, thickness):
    """Dibuja el contorno cerrado de un polígono."""
    if len(points) >= 2:
        pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(img, [pts], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)

def fill_polygon(img, points, color):
    """Rellena el interior de un polígono cerrado."""
    if len(points) >= 3:
        pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(img, [pts], color, lineType=cv2.LINE_AA)