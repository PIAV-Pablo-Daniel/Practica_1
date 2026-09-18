from turtle import color

import cv2
import tkinter as tk
import drawing_tools
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

        self.rgb_label = tk.Label(root, text="RGB: —")
        self.rgb_label.pack()

        self.image_label.bind("<Motion>", self.on_mouse_move)
        self.image_label.bind("<ButtonPress-1>", self.on_press)
        self.image_label.bind("<B1-Motion>", self.on_drag)
        self.image_label.bind("<ButtonRelease-1>", self.on_release)

        self.tool = tk.StringVar(value="line")
        self.color_rgb = (255, 0, 0)
        self.thickness = tk.IntVar(value=2)
        self.fill_enabled = tk.BooleanVar(value=False)
        self.start_point = None
        self.preview_image = None

        self.build_toolbar()

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
        self.show_array(self.image)

    def show_array(self, array):
        rgb = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        self.tk_image = ImageTk.PhotoImage(pil)
        self.image_label.config(image=self.tk_image)

    def on_mouse_move(self, event):
        if self.image is None:
            return
        h, w = self.image.shape[:2]
        x, y = event.x, event.y
        if 0 <= x < w and 0 <= y < h:
            b, g, r = self.image[y, x]
            self.rgb_label.config(text=f"RGB: ({r}, {g}, {b})")
        else:
            self.rgb_label.config(text="RGB: —")

    def build_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack()

        # Selección de herramienta
        tools = [
            ("Línea", "line"),
            ("Rectángulo", "rectangle"),
            ("Círculo", "circle"),
            ("Elipse", "ellipse"),
            ("Polilínea", "polyline"),
            ("Polígono", "polygon"),
        ]
        for label, value in tools:
            tk.Radiobutton(
                toolbar, text=label, variable=self.tool, value=value
            ).pack(side="left")

        # Color RGB
        self.r_value = tk.IntVar(value=255)
        self.g_value = tk.IntVar(value=0)
        self.b_value = tk.IntVar(value=0)

        tk.Label(toolbar, text="R:").pack(side="left")
        tk.Spinbox(toolbar, from_=0, to=255, width=4, textvariable=self.r_value).pack(side="left")
        tk.Label(toolbar, text="G:").pack(side="left")
        tk.Spinbox(toolbar, from_=0, to=255, width=4, textvariable=self.g_value).pack(side="left")
        tk.Label(toolbar, text="B:").pack(side="left")
        tk.Spinbox(toolbar, from_=0, to=255, width=4, textvariable=self.b_value).pack(side="left")

        # Grosor
        tk.Label(toolbar, text="Grosor:").pack(side="left")
        tk.Spinbox(toolbar, from_=1, to=50, width=4, textvariable=self.thickness).pack(side="left")

        # Relleno
        tk.Checkbutton(toolbar, text="Rellenar", variable=self.fill_enabled).pack(side="left")

    def get_bgr_color(self):
        def clamp_channel(value_var):
            try:
                v = int(value_var.get())
            except (tk.TclError, TypeError, ValueError):
                v = 0
            v = max(0, min(255, v))
            value_var.set(v)
            return v

        r = clamp_channel(self.r_value)
        g = clamp_channel(self.g_value)
        b = clamp_channel(self.b_value)
        return (b, g, r)

    def get_thickness(self):
        try:
            t = int(self.thickness.get())
        except (tk.TclError, TypeError, ValueError):
            t = 1
        t = max(1, min(50, t))
        self.thickness.set(t)
        return t

    def on_press(self, event):
        if self.image is None:
            return
        self.start_point = (event.x, event.y)

    def on_drag(self, event):
        if self.image is None or self.start_point is None:
            return
        preview = self.image.copy()
        self.draw_current_shape(preview, self.start_point, (event.x, event.y))
        self.show_array(preview)
        

    def on_release(self, event):
        if self.image is None or self.start_point is None:
            return
        self.draw_current_shape(self.image, self.start_point, (event.x, event.y))
        self.start_point = None
        self.refresh_view()

    def draw_current_shape(self, img, p1, p2):
        tool = self.tool.get()
        color = self.get_bgr_color()
        thickness = self.get_thickness()

        if tool == "line":
            drawing_tools.draw_line(img, p1, p2, color, thickness)
        elif tool == "rectangle":
            drawing_tools.draw_rectangle(img, p1, p2, color, thickness)
        elif tool == "circle":
            drawing_tools.draw_circle(img, p1, p2, color, thickness)