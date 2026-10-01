# Práctica 1 — Procesamiento de Imágenes, Audio y Vídeo (PIAV)

**Autores:** Pablo Martínez Suárez & Daniel Rodríguez Alonso  
**Tecnologías:** Python 3, OpenCV (`cv2`), Tkinter, NumPy, Pillow.

---

## 1. Resumen de la Práctica

Aplicación gráfica interactiva desarrollada con **Tkinter** y **OpenCV** para la visualización, inspección y edición gráfica de imágenes. El diseño se ha simplificado al máximo para contener únicamente el código estrictamente necesario para cumplir con el 100% de los requisitos del enunciado, manteniendo un sistema robusto de **zoom, escala interactiva y barras de desplazamiento** que permite trabajar con imágenes de cualquier resolución sin desbordamientos de pantalla.

### Cumplimiento del Enunciado

| Requisito | Descripción | Implementación |
| :--- | :--- | :--- |
| **1a. Obligatorio (2.5 pts)** | Cargar imagen y mostrar el valor RGB del píxel bajo el cursor | Evento `<Motion>` en el Canvas que indexa la matriz NumPy `img[y, x]` y muestra `RGB: (R, G, B)` adaptado a zoom y scroll |
| **1b. Obligatorio (2.5 pts)** | Dibujar líneas, rectángulos y círculos con color RGB y grosor | En `drawing_tools.py`, con selectores RGB (0-255), grosor (1-50) y previsualización en vivo (doble búfer volátil) |
| **2.1. Optativo (1.25 pts)** | Figuras rellenas seleccionables en la interfaz | Checkbox *Rellenar figura* (`cv2.FILLED` y `cv2.fillPoly`) |
| **2.2. Optativo (1.25 pts)** | Otras primitivas: elipses, polilíneas y polígonos | Creadas interactivamente con ratón y cierre por doble clic o botón |
| **2.3. Optativo (1.25 pts)** | Guardar dibujo como vídeo paso a paso | Botón *Grabar vídeo* que genera un archivo `.mp4` con `video_recorder.py` |
| **2.4. Optativo (1.25 pts)** | Aportación propia | **Redimensión / Escala interactiva** (25%-300% con autoajuste a ventana para imágenes gigantes) + **Deshacer** (`Ctrl+Z`) |

---

## 2. Estructura de Archivos

Diseño modular limpio y conciso en solo 4 archivos de código:

```text
Practica_1/
├── main.py             # Punto de entrada de la aplicación (7 líneas)
├── app.py              # Interfaz gráfica Tkinter, control del ratón y zoom/scroll (~230 líneas)
├── drawing_tools.py    # Funciones analíticas de dibujo con OpenCV (~35 líneas)
├── video_recorder.py   # Generación del vídeo MP4 paso a paso (~15 líneas)
├── README.md           # Resumen y guía de uso
├── Memoria_Practica_1_PIAV.pdf      # Memoria técnica formal
└── Guia_Defensa_Practica_1_PIAV.pdf # Guía rápida para la defensa oral
```

---

## 3. Instalación y Ejecución

```bash
# Con uv (recomendado)
uv run python main.py

# O con Python directamente
python3 main.py
```

---

## 4. Uso Rápido de la Aplicación

1. **Abrir imagen:** Pulsa **"Abrir imagen"**. Si la imagen es grande, el programa la ajusta automáticamente a las dimensiones de la pantalla.
2. **Escala y Navegación:**
   - Desliza el control **Zoom / Escala** (25% - 300%).
   - Pulsa **"Ajustar a ventana"** para encajarla automáticamente o **"100%"** para tamaño nativo.
   - Si la imagen excede la ventana, puedes desplazarte con las barras de scroll horizontal y vertical.
3. **Inspección de Píxel (1a):** Mueve el cursor sobre la imagen para ver las coordenadas exactas `(x, y)` y la terna `RGB: (R, G, B)`.
4. **Dibujo de Primitivas (1b, 2.1, 2.2):**
   - Elige la herramienta deseada: Línea, Rectángulo, Círculo, Elipse, Polilínea o Polígono.
   - Ajusta el color (R, G, B de 0 a 255) y el grosor del trazo.
   - Marca "Rellenar figura" para figuras sólidas.
   - Arrastra con el ratón para trazar figuras simples (doble búfer para previsualización limpia).
   - Para polilíneas y polígonos, haz clics sucesivos y haz doble clic para cerrar.
5. **Grabación de Vídeo (2.3):** Pulsa **"Grabar vídeo"** antes de empezar a dibujar. Al finalizar, pulsa **"Detener grabación"** para guardar el `.mp4`.
6. **Deshacer:** Pulsa **"Deshacer"** o `Ctrl+Z` para revertir trazos.
