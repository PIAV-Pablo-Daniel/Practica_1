import cv2


def draw_line(img, p1, p2, color, thickness):
    cv2.line(img, p1, p2, color, thickness, lineType=cv2.LINE_AA)

def draw_rectangle(img, p1, p2, color, thickness):
    cv2.rectangle(img, p1, p2, color, thickness)


def draw_circle(img, p1, p2, color, thickness):
    cx, cy = p1
    x2, y2 = p2
    radius = int(((x2 - cx) ** 2 + (y2 - cy) ** 2) ** 0.5)
    cv2.circle(img, (cx, cy), radius, color, thickness, lineType=cv2.LINE_AA)