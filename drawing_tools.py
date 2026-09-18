import cv2
import numpy as np

def draw_line(img, p1, p2, color, thickness):
    cv2.line(img, p1, p2, color, thickness, lineType=cv2.LINE_AA)

def draw_rectangle(img, p1, p2, color, thickness):
    cv2.rectangle(img, p1, p2, color, thickness)


def draw_circle(img, p1, p2, color, thickness):
    cx, cy = p1
    x2, y2 = p2
    radius = int(((x2 - cx) ** 2 + (y2 - cy) ** 2) ** 0.5)
    cv2.circle(img, (cx, cy), radius, color, thickness, lineType=cv2.LINE_AA)

def draw_ellipse(img, p1, p2, color, thickness):
    x1, y1 = p1
    x2, y2 = p2
    center = ((x1 + x2) // 2, (y1 + y2) // 2)
    axes = (abs(x2 - x1) // 2, abs(y2 - y1) // 2)
    cv2.ellipse(img, center, axes, 0, 0, 360, color, thickness, lineType=cv2.LINE_AA)

def draw_polyline(img, points, color, thickness):
    pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [pts], isClosed=False, color=color, thickness=thickness, lineType=cv2.LINE_AA)


def draw_polygon(img, points, color, thickness):
    pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [pts], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)


def fill_polygon(img, points, color):
    pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(img, [pts], color, lineType=cv2.LINE_AA)