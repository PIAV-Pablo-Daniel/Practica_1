import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

import drawing_tools
import video_recorder
import utils


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PIAV - Práctica 1: Visor y Editor Gráfico")
        self.root.geometry("1100x720")

        # Imagen maestra en formato OpenCV (BGR) y copia original de respaldo
        self.image = None
        self.original_image = None
        self.scale_factor = 1.0

        # Historial de cambios para Deshacer (Undo)
        self.history = []

        # Grabación de vídeo paso a paso
        self.recording = False
        self.recorded_frames = []

        # Configuración de dibujo
        self.tool = tk.StringVar(value="line")
        self.fill_enabled = tk.BooleanVar(value=False)
        self.thickness = tk.IntVar(value=2)
        self.r_val = tk.IntVar(value=255)
        self.g_val = tk.IntVar(value=0)
        self.b_val = tk.IntVar(value=0)

        # Control del ratón
        self.start_point = None
        self.poly_points = []

        # Interfaz de usuario y atajos de teclado
        self.setup_ui()
        self.root.bind("<Control-z>", lambda e: self.undo())

    def setup_ui(self):
        # 1. Barra superior: Acciones, Zoom, Grabación, Deshacer y Filtros
        top_bar = tk.Frame(self.root, bd=1, relief=tk.RAISED, padx=5, pady=4)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(top_bar, text="Abrir", command=self.open_image).pack(side=tk.LEFT, padx=2)
        tk.Button(top_bar, text="Guardar", command=self.save_image).pack(side=tk.LEFT, padx=2)
        tk.Button(top_bar, text="Restaurar", command=self.restore_original).pack(side=tk.LEFT, padx=2)
        tk.Button(top_bar, text="Deshacer (Ctrl+Z)", command=self.undo).pack(side=tk.LEFT, padx=2)

        # Control de Escala / Zoom
        f_zoom = tk.LabelFrame(top_bar, text="Zoom / Escala", padx=4, pady=1)
        f_zoom.pack(side=tk.LEFT, padx=6)
        self.scale_var = tk.DoubleVar(value=100.0)
        tk.Scale(
            f_zoom, from_=25, to=300, orient=tk.HORIZONTAL, variable=self.scale_var,
            command=lambda e: self.refresh_view(), length=100
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(f_zoom, text="100%", command=lambda: [self.scale_var.set(100.0), self.refresh_view()]).pack(side=tk.LEFT, padx=2)
        tk.Button(f_zoom, text="Ajustar", command=self.fit_to_window).pack(side=tk.LEFT, padx=2)

        self.record_btn = tk.Button(top_bar, text="Grabar vídeo", command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, padx=6)

        # Filtros (Aportación propia)
        tk.Label(top_bar, text="Filtro:").pack(side=tk.LEFT, padx=(6, 2))
        self.filter_var = tk.StringVar(value="Escala de Grises")
        filter_combo = ttk.Combobox(
            top_bar, textvariable=self.filter_var,
            values=["Escala de Grises", "Desenfoque (Blur)", "Bordes (Canny)", "Invertir Colores"],
            state="readonly", width=16
        )
        filter_combo.pack(side=tk.LEFT, padx=2)
        tk.Button(top_bar, text="Aplicar", command=self.apply_filter).pack(side=tk.LEFT, padx=2)

        # 2. Panel lateral: Herramientas, Opciones, Color e Inspector RGB
        side_panel = tk.Frame(self.root, width=220, bd=1, relief=tk.RAISED, padx=8, pady=6)
        side_panel.pack(side=tk.LEFT, fill=tk.Y)
        side_panel.pack_propagate(False)

        # Selección de herramienta
        f_tools = tk.LabelFrame(side_panel, text="Herramientas", padx=5, pady=4)
        f_tools.pack(fill=tk.X, pady=4)
        tools = [("Línea", "line"), ("Rectángulo", "rectangle"), ("Círculo", "circle"),
                 ("Elipse", "ellipse"), ("Polilínea", "polyline"), ("Polígono", "polygon")]
        for text, val in tools:
            tk.Radiobutton(f_tools, text=text, variable=self.tool, value=val, anchor="w").pack(fill=tk.X)
        tk.Button(f_tools, text="Cerrar polígono (Doble Clic)", command=self.finish_polygon).pack(fill=tk.X, pady=3)

        # Opciones de dibujo
        f_opts = tk.LabelFrame(side_panel, text="Propiedades", padx=5, pady=4)
        f_opts.pack(fill=tk.X, pady=4)
        tk.Checkbutton(f_opts, text="Rellenar figura", variable=self.fill_enabled).pack(anchor="w")

        thick_row = tk.Frame(f_opts)
        thick_row.pack(fill=tk.X, pady=2)
        tk.Label(thick_row, text="Grosor:").pack(side=tk.LEFT)
        tk.Spinbox(thick_row, from_=1, to=50, width=5, textvariable=self.thickness).pack(side=tk.RIGHT)

        # Color en RGB
        f_color = tk.LabelFrame(side_panel, text="Color (RGB)", padx=5, pady=4)
        f_color.pack(fill=tk.X, pady=4)
        for label, var in [("R (Rojo):", self.r_val), ("G (Verde):", self.g_val), ("B (Azul):", self.b_val)]:
            row = tk.Frame(f_color)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=label, width=9, anchor="w").pack(side=tk.LEFT)
            tk.Spinbox(row, from_=0, to=255, width=4, textvariable=var).pack(side=tk.RIGHT)
            var.trace_add("write", lambda *_: self.update_color_preview())

        self.color_preview = tk.Canvas(f_color, height=20, bd=1, relief=tk.SUNKEN)
        self.color_preview.pack(fill=tk.X, pady=4)
        self.update_color_preview()

        # Inspector de Píxel (Requisito 1a)
        f_pixel = tk.LabelFrame(side_panel, text="Inspector de Píxel", padx=5, pady=6)
        f_pixel.pack(fill=tk.X, pady=6)
        self.pos_label = tk.Label(f_pixel, text="Posición: —", anchor="w")
        self.pos_label.pack(fill=tk.X)
        self.rgb_label = tk.Label(f_pixel, text="RGB: —", font=("Consolas", 10, "bold"), anchor="w", fg="#004488")
        self.rgb_label.pack(fill=tk.X, pady=2)

        # 3. Canvas central con barras de desplazamiento
        center_frame = tk.Frame(self.root)
        center_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(center_frame, bg="#333333", cursor="crosshair")
        vbar = tk.Scrollbar(center_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        hbar = tk.Scrollbar(center_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Eventos del ratón sobre la imagen
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", lambda e: self.finish_polygon())

    # --- Gestión de Coordenadas, Color y Zoom ---
    def get_coords(self, event):
        """Convierte coordenadas del canvas (con scroll y zoom) a píxeles reales de la imagen."""
        if self.image is None:
            return None
        # Desplazamiento por scroll y escalado por zoom
        x = int(self.canvas.canvasx(event.x) / self.scale_factor)
        y = int(self.canvas.canvasy(event.y) / self.scale_factor)
        h, w = self.image.shape[:2]
        if 0 <= x < w and 0 <= y < h:
            return (x, y)
        return None

    def get_bgr_color(self):
        """Devuelve el color seleccionado en orden BGR para OpenCV."""
        r = max(0, min(255, int(self.r_val.get())))
        g = max(0, min(255, int(self.g_val.get())))
        b = max(0, min(255, int(self.b_val.get())))
        return (b, g, r)

    def update_color_preview(self):
        try:
            r = max(0, min(255, int(self.r_val.get())))
            g = max(0, min(255, int(self.g_val.get())))
            b = max(0, min(255, int(self.b_val.get())))
            self.color_preview.config(bg=f"#{r:02x}{g:02x}{b:02x}")
        except Exception:
            pass

    def refresh_view(self, preview_img=None):
        """Muestra en Tkinter la imagen escalada según el zoom configurado por el usuario."""
        base = self.image if preview_img is None else preview_img
        if base is None:
            return

        self.scale_factor = max(0.25, self.scale_var.get() / 100.0)
        h, w = base.shape[:2]
        nw, nh = max(1, int(w * self.scale_factor)), max(1, int(h * self.scale_factor))

        disp = base if (nw == w and nh == h) else cv2.resize(base, (nw, nh), interpolation=cv2.INTER_LINEAR)
        rgb_img = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(rgb_img))

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=(0, 0, nw, nh))

    def fit_to_window(self):
        """Calcula el porcentaje de escala para que la imagen se ajuste a la ventana visible."""
        if self.image is None:
            return
        cw, ch = max(50, self.canvas.winfo_width()), max(50, self.canvas.winfo_height())
        h, w = self.image.shape[:2]
        scale = min(cw / w, ch / h) * 98.0
        self.scale_var.set(round(max(25.0, min(300.0, scale)), 1))
        self.refresh_view()

    # --- Requisito 1a: Inspector RGB al mover el ratón ---
    def on_mouse_move(self, event):
        coords = self.get_coords(event)
        if coords is None:
            return
        x, y = coords
        # En OpenCV la matriz se indexa como [y, x] y el orden es (Azul, Verde, Rojo)
        b, g, r = self.image[y, x]
        self.pos_label.config(text=f"Posición: ({x}, {y})")
        self.rgb_label.config(text=f"RGB: ({int(r)}, {int(g)}, {int(b)})")

    # --- Requisito 1b y 2: Dibujo de Primitivas con el Ratón ---
    def on_press(self, event):
        coords = self.get_coords(event)
        if coords is None:
            return

        if self.tool.get() in ("polyline", "polygon"):
            self.poly_points.append(coords)
            self.update_poly_preview()
        else:
            self.start_point = coords

    def on_drag(self, event):
        """Previsualiza la figura en una copia en memoria sin modificar la imagen original."""
        if self.image is None or self.start_point is None or self.tool.get() in ("polyline", "polygon"):
            return
        coords = self.get_coords(event)
        if coords:
            preview = self.image.copy()
            self.draw_shape(preview, self.start_point, coords)
            self.refresh_view(preview_img=preview)

    def on_release(self, event):
        """Plasma la figura definitiva en la imagen al soltar el ratón."""
        if self.image is None or self.start_point is None or self.tool.get() in ("polyline", "polygon"):
            return
        coords = self.get_coords(event)
        if coords:
            self.push_history()
            self.draw_shape(self.image, self.start_point, coords)
            self.capture_video_frame()
            self.refresh_view()
        self.start_point = None

    def draw_shape(self, target_img, p1, p2):
        tool = self.tool.get()
        color = self.get_bgr_color()
        thick = cv2.FILLED if self.fill_enabled.get() else max(1, self.thickness.get())

        if tool == "line":
            drawing_tools.draw_line(target_img, p1, p2, color, max(1, self.thickness.get()))
        elif tool == "rectangle":
            drawing_tools.draw_rectangle(target_img, p1, p2, color, thick)
        elif tool == "circle":
            drawing_tools.draw_circle(target_img, p1, p2, color, thick)
        elif tool == "ellipse":
            drawing_tools.draw_ellipse(target_img, p1, p2, color, thick)

    def update_poly_preview(self):
        """Muestra los vértices y segmentos actuales de la polilínea o polígono."""
        if not self.poly_points or self.image is None:
            return
        preview = self.image.copy()
        color = self.get_bgr_color()
        thick = max(1, self.thickness.get())
        for pt in self.poly_points:
            cv2.circle(preview, pt, max(2, thick), color, cv2.FILLED)
        drawing_tools.draw_polyline(preview, self.poly_points, color, thick)
        self.refresh_view(preview_img=preview)

    def finish_polygon(self):
        """Finaliza el trazado de polilínea o polígono."""
        if self.image is None or self.tool.get() not in ("polyline", "polygon") or len(self.poly_points) < 2:
            self.poly_points.clear()
            self.refresh_view()
            return

        # Descartamos clic duplicado habitual del doble clic
        if len(self.poly_points) >= 2 and self.poly_points[-1] == self.poly_points[-2]:
            self.poly_points.pop()

        self.push_history()
        color = self.get_bgr_color()
        thick = max(1, self.thickness.get())

        if self.tool.get() == "polyline":
            drawing_tools.draw_polyline(self.image, self.poly_points, color, thick)
        else:
            if self.fill_enabled.get():
                drawing_tools.fill_polygon(self.image, self.poly_points, color)
            else:
                drawing_tools.draw_polygon(self.image, self.poly_points, color, thick)

        self.capture_video_frame()
        self.poly_points.clear()
        self.refresh_view()

    # --- Aportación propia: Filtros OpenCV y Deshacer ---
    def apply_filter(self):
        if self.image is None:
            messagebox.showinfo("Aviso", "Primero abre una imagen.")
            return
        self.push_history()
        self.image = utils.apply_filter(self.image, self.filter_var.get())
        self.capture_video_frame()
        self.refresh_view()

    def push_history(self):
        if self.image is not None:
            self.history.append(self.image.copy())
            if len(self.history) > 20:
                self.history.pop(0)

    def undo(self):
        if self.history:
            self.image = self.history.pop()
            self.poly_points.clear()
            self.refresh_view()

    # --- Archivos y Grabación de Vídeo ---
    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if not path:
            return
        try:
            self.image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        except Exception:
            self.image = cv2.imread(path)

        if self.image is None:
            messagebox.showerror("Error", "No se pudo cargar la imagen.")
            return

        self.original_image = self.image.copy()
        self.history.clear()
        self.poly_points.clear()
        self.start_point = None

        # Si la imagen es grande, ajustamos automáticamente para verla entera
        h, w = self.image.shape[:2]
        if w > 850 or h > 600:
            scale = min(850.0 / w, 600.0 / h) * 100.0
            self.scale_var.set(round(scale, 1))
        else:
            self.scale_var.set(100.0)

        self.refresh_view()

    def save_image(self):
        if self.image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if not path:
            return
        ext = os.path.splitext(path)[1] or ".png"
        success, buf = cv2.imencode(ext, self.image)
        if success:
            buf.tofile(path)

    def restore_original(self):
        if self.original_image is not None:
            self.push_history()
            self.image = self.original_image.copy()
            self.poly_points.clear()
            self.refresh_view()

    def toggle_recording(self):
        if self.image is None:
            return
        self.recording = not self.recording
        if self.recording:
            self.recorded_frames = [self.image.copy()]
            self.record_btn.config(text="Detener grabación", bg="#ffaaaa")
        else:
            self.record_btn.config(text="Grabar vídeo", bg="SystemButtonFace")
            self.save_video()

    def capture_video_frame(self):
        if self.recording and self.image is not None:
            self.recorded_frames.append(self.image.copy())

    def save_video(self):
        if not self.recorded_frames:
            return
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("Vídeo MP4", "*.mp4")])
        if path:
            if video_recorder.write_video(path, self.recorded_frames):
                messagebox.showinfo("Vídeo guardado", f"Vídeo paso a paso guardado en:\n{path}")
            else:
                messagebox.showerror("Error", "No se pudo crear el vídeo.")