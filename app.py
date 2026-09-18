from turtle import color

import cv2
import numpy as np
import tkinter as tk
import drawing_tools
import video_recorder
from tkinter import filedialog
from PIL import Image, ImageTk


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PIAV - Práctica 1")
        self.image = None
        self.original_image = None
        self.recording = False
        self.recorded_frames = []
        self.tk_image = None

        self.image_label = tk.Label(root)
        self.image_label.pack()

        open_btn = tk.Button(root, text="Abrir imagen", command=self.open_image)
        open_btn.pack()

        save_btn = tk.Button(root, text="Guardar imagen", command=self.save_image)
        save_btn.pack()

        restore_btn = tk.Button(root, text="Restaurar", command=self.restore_original)
        restore_btn.pack()

        self.record_btn = tk.Button(root, text="Iniciar grabación", command=self.toggle_recording)
        self.record_btn.pack()

        self.rgb_label = tk.Label(root, text="RGB: —")
        self.rgb_label.pack()

        self.hex_label = tk.Label(root, text="HEX: —")
        self.hex_label.pack()

        self.hsv_label = tk.Label(root, text="HSV: —")
        self.hsv_label.pack()

        self.luminance_label = tk.Label(root, text="Luminancia: —")
        self.luminance_label.pack()

        self.zoom_label = tk.Label(root)
        self.zoom_label.pack()
        self.zoom_tk_image = None


        self.image_label.bind("<Motion>", self.on_mouse_move)
        self.image_label.bind("<ButtonPress-1>", self.on_press)
        self.image_label.bind("<B1-Motion>", self.on_drag)
        self.image_label.bind("<ButtonRelease-1>", self.on_release)
        self.image_label.bind("<Double-Button-1>", lambda event: self.finish_polygon())

        self.tool = tk.StringVar(value="line")
        self.color_rgb = (255, 0, 0)
        self.thickness = tk.IntVar(value=2)
        self.fill_enabled = tk.BooleanVar(value=False)
        self.start_point = None
        self.poly_points = []
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
        self.original_image = img.copy()
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
            r, g, b = int(r), int(g), int(b)

            self.rgb_label.config(text=f"RGB: ({r}, {g}, {b})")
            self.hex_label.config(text=f"HEX: #{r:02X}{g:02X}{b:02X}")

            pixel_bgr = np.uint8([[[b, g, r]]])
            hsv = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2HSV)[0, 0]
            h_val, s_val, v_val = map(int, hsv)
            self.hsv_label.config(text=f"HSV: ({h_val}, {s_val}, {v_val})")

            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            self.luminance_label.config(text=f"Luminancia: {luminance:.1f}")

            self.update_zoom(x, y)
        else:
            self.rgb_label.config(text="RGB: —")
            self.hex_label.config(text="HEX: —")
            self.hsv_label.config(text="HSV: —")
            self.luminance_label.config(text="Luminancia: —")

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
        tk.Button(toolbar, text="Finalizar figura", command=self.finish_polygon).pack(side="left")

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
        tool = self.tool.get()
        if tool in ("polyline", "polygon"):
            self.poly_points.append((event.x, event.y))
            self.update_poly_preview()
        else:
            self.start_point = (event.x, event.y)

    def on_drag(self, event):
        if self.image is None or self.start_point is None:
            return
        tool = self.tool.get()
        if tool in ("polyline", "polygon"):
            return
        preview = self.image.copy()
        self.draw_current_shape(preview, self.start_point, (event.x, event.y))
        self.show_array(preview)


    def on_release(self, event):
        if self.image is None or self.start_point is None:
            return
        tool = self.tool.get()
        if tool in ("polyline", "polygon"):
            return
        self.draw_current_shape(self.image, self.start_point, (event.x, event.y))
        self.capture_frame()
        self.start_point = None
        self.refresh_view()

    def draw_current_shape(self, img, p1, p2):
        tool = self.tool.get()
        color = self.get_bgr_color()
        thickness = self.get_thickness()
        fillable = tool in ("rectangle", "circle")
        draw_thickness = cv2.FILLED if (fillable and self.fill_enabled.get()) else thickness

        if tool == "line":
            drawing_tools.draw_line(img, p1, p2, color, thickness)
        elif tool == "rectangle":
            drawing_tools.draw_rectangle(img, p1, p2, color, draw_thickness)
        elif tool == "circle":
            drawing_tools.draw_circle(img, p1, p2, color, draw_thickness)
        elif tool == "ellipse":
            drawing_tools.draw_ellipse(img, p1, p2, color, draw_thickness)

    def update_poly_preview(self):
        if not self.poly_points:
            return
        preview = self.image.copy()
        color = self.get_bgr_color()
        thickness = self.get_thickness()
        for point in self.poly_points:
            cv2.circle(preview, point, 3, color, cv2.FILLED, cv2.LINE_AA)
        if len(self.poly_points) > 1:
            drawing_tools.draw_polyline(preview, self.poly_points, color, thickness)
        self.show_array(preview)

    def finish_polygon(self):
        tool = self.tool.get()
        if tool not in ("polyline", "polygon"):
            return
        # el doble clic genera dos clics casi en el mismo punto; se descarta el duplicado
        if len(self.poly_points) >= 2 and self.poly_points[-1] == self.poly_points[-2]:
            self.poly_points.pop()
        if len(self.poly_points) < 2:
            self.poly_points = []
            self.refresh_view()
            return

        color = self.get_bgr_color()
        thickness = self.get_thickness()

        if tool == "polyline":
            drawing_tools.draw_polyline(self.image, self.poly_points, color, thickness)
        else:  # polygon
            if self.fill_enabled.get():
                drawing_tools.fill_polygon(self.image, self.poly_points, color)
            else:
                drawing_tools.draw_polygon(self.image, self.poly_points, color, thickness)

        self.capture_frame()
        self.poly_points = []
        self.refresh_view()

    def update_zoom(self, x, y):
        h, w = self.image.shape[:2]
        radius = 5
        x1, x2 = max(0, x - radius), min(w, x + radius + 1)
        y1, y2 = max(0, y - radius), min(h, y + radius + 1)
        patch = self.image[y1:y2, x1:x2]

        zoom = cv2.resize(patch, None, fx=12, fy=12, interpolation=cv2.INTER_NEAREST)
        zoom_rgb = cv2.cvtColor(zoom, cv2.COLOR_BGR2RGB)
        pil_zoom = Image.fromarray(zoom_rgb)
        self.zoom_tk_image = ImageTk.PhotoImage(pil_zoom)
        self.zoom_label.config(image=self.zoom_tk_image)

    def save_image(self):
        if self.image is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        if not path:
            return
        cv2.imwrite(path, self.image)

    def restore_original(self):
        if self.original_image is None:
            return
        self.image = self.original_image.copy()
        self.refresh_view()

    def toggle_recording(self):
        if self.image is None:
            return
        if not self.recording:
            self.recording = True
            self.recorded_frames = []
            self.capture_frame()
            self.record_btn.config(text="Detener grabación")
        else:
            self.recording = False
            self.record_btn.config(text="Iniciar grabación")
            self.save_video()


    def capture_frame(self):
        if self.recording and self.image is not None:
            self.recorded_frames.append(self.image.copy())


    def save_video(self):
        if not self.recorded_frames:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4")]
        )
        if not path:
            return
        video_recorder.write_video(path, self.recorded_frames)

    