import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PIAV - Práctica 1")
        self.image = None
        self.tk_image = None

        self.image_label = tk.Label(root)
        self.image_label.pack()

        open_btn = tk.Button(root, text="Abrir imagen", command=self.open_image)
        open_btn.pack()

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")]
        )
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            return
        self.image = img
        self.refresh_view()

    def refresh_view(self):
        rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        self.tk_image = ImageTk.PhotoImage(pil)
        self.image_label.config(image=self.tk_image)