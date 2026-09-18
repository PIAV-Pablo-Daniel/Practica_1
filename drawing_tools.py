import cv2


def draw_line(img, p1, p2, color, thickness):
    cv2.line(img, p1, p2, color, thickness, lineType=cv2.LINE_AA)