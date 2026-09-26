# Práctica 1 — Procesamiento de Imágenes, Audio y Vídeo (PIAV)

**Autores:** Pablo Martínez Suárez & Daniel Rodríguez Alonso  
**Tecnologías:** Python 3, OpenCV (`cv2`), Tkinter, NumPy, Pillow.

---

## 1. Resumen de la Práctica

Aplicación gráfica interactiva desarrollada con **Tkinter** y **OpenCV** que permite cargar imágenes, inspeccionar el valor RGB de cualquier píxel en tiempo real y dibujar diferentes primitivas geométricas con el ratón. Además, incluye control interactivo de escala y zoom, grabación del proceso en vídeo paso a paso y filtros de procesamiento digital de imágenes como aportación propia.

### Cumplimiento del Enunciado

| Requisito | Descripción | Implementación |
| :--- | :--- | :--- |
| **1a. Obligatorio (2.5 pts)** | Cargar imagen y mostrar el valor RGB del píxel bajo el cursor | Evento `<Motion>` en el Canvas que lee `img[y, x]` y muestra `RGB: (R, G, B)` con mapeo exacto de zoom y scroll |
| **1b. Obligatorio (2.5 pts)** | Dibujar líneas, rectángulos, círculos con color RGB y grosor | En `drawing_tools.py` con previsualización en vivo sin ensuciar la imagen |
| **2.1. Optativo (1.25 pts)** | Figuras rellenas seleccionables en la interfaz | Checkbox *Rellenar figura* (`cv2.FILLED` y `cv2.fillPoly`) |
| **2.2. Optativo (1.25 pts)** | Otras primitivas: elipses, polilíneas y polígonos | Creadas con ratón; cierre por doble clic o botón |
| **2.3. Optativo (1.25 pts)** | Guardar dibujo como vídeo paso a paso | Botón *Grabar vídeo* que genera un archivo `.mp4` con `video_recorder.py` |
| **2.4. Optativo (1.25 pts)** | Aportación propia | Filtros OpenCV (Grises, Blur, Canny, Invertir) + Control de Zoom/Escala a medida (25%-300% y Ajuste automático) + Deshacer (Ctrl+Z) |

---

## 2. Estructura de Archivos

El proyecto está dividido en módulos sencillos con responsabilidades bien definidas:

```text
Practica_1/
├── main.py             # Punto de entrada: crea la ventana y arranca DrawingApp (7 líneas)
├── app.py              # Interfaz gráfica (Tkinter), zoom/escala y eventos del ratón (~270 líneas)
├── drawing_tools.py    # Funciones de trazado de figuras con OpenCV (cv2) (~45 líneas)
├── utils.py            # Filtros de imagen clásicos de OpenCV (Aportación propia) (~25 líneas)
├── video_recorder.py   # Grabación del proceso de dibujo en vídeo MP4 (~20 líneas)
├── README.md           # Documentación sencilla del proyecto
└── Guia_Defensa_Practica_1_PIAV.pdf # Guía resumida para la defensa oral (4 páginas)
```

---

## 3. Instalación y Ejecución

Con el entorno virtual activado o directamente con Python:

```bash
# Ejecutar la aplicación
python main.py
```

Dependencias principales: `opencv-python`, `pillow`, `numpy`, `reportlab`.

---

## 4. Funcionamiento y Uso de la Interfaz

1. **Abrir imagen:** Pulsa **"Abrir"** y selecciona cualquier archivo (`.png`, `.jpg`, `.bmp`, etc.). Si la imagen es grande, el programa la reescala automáticamente para que quepa en la ventana sin perder resolución en la matriz original.
2. **Escala y Zoom a gusto del usuario:**
   - Usa el deslizador horizontal **Zoom / Escala** para ampliar o reducir la visualización entre el 25% y el 300%.
   - Pulsa el botón **"Ajustar"** para encajarla automáticamente en la ventana visible.
   - Pulsa el botón **"100%"** para volver a la escala original real píxel a píxel.
   - Todo el dibujo, las coordenadas y el inspector se adaptan automáticamente a la escala seleccionada.
3. **Inspeccionar píxeles (Requisito 1a):** Mueve el ratón sobre la imagen: en el panel izquierdo verás la posición `(x, y)` real de la matriz y el triplete exacto `RGB: (R, G, B)`.
4. **Elegir herramienta y propiedades:**
   - Selecciona la figura: **Línea**, **Rectángulo**, **Círculo**, **Elipse**, **Polilínea** o **Polígono**.
   - Ajusta el color en los selectores **R**, **G** y **B** (de 0 a 255).
   - Ajusta el **Grosor** del trazo (1 a 50).
   - Marca **"Rellenar figura"** si deseas que figuras cerradas queden rellenas de color.
5. **Dibujar sobre el lienzo (Requisitos 1b y 2.2):**
   - Para figuras simples (Línea, Rectángulo, Círculo, Elipse): haz clic, arrastra para ver la figura en tiempo real y suelta para confirmarla.
   - Para figuras compuestas (Polilínea, Polígono): haz clic en varios puntos para añadir vértices y haz **doble clic** (o pulsa *"Cerrar polígono"*) para terminarla.
6. **Grabar vídeo (Requisito 2.3):**
   - Pulsa **"Grabar vídeo"** antes de empezar a dibujar.
   - Realiza varios trazos o dibujos.
   - Vuelve a pulsar el botón para detener y guardar el resultado como un archivo `.mp4` visualizable paso a paso.
7. **Aportación propia (Filtros, Zoom y Deshacer):**
   - Elige un filtro en el desplegable (*Escala de Grises*, *Desenfoque*, *Bordes Canny*, *Invertir*) y pulsa **"Aplicar"**.
   - Usa **"Deshacer"** (o `Ctrl+Z`) para revertir trazos o filtros.
   - Usa **"Restaurar"** para regresar a la imagen inicial.

---

## 5. Conceptos Clave para la Defensa

- **Mapeo de Coordenadas con Zoom y Scroll:** Cuando la imagen está escalada o tiene barras de desplazamiento, la coordenada del cursor en pantalla no coincide con el píxel real. Se calcula como `x = int(canvas.canvasx(event.x) / scale_factor)`, asegurando que siempre se lee y dibuja sobre el píxel exacto de la matriz original sin distorsiones.
- **BGR vs RGB:** OpenCV lee y almacena imágenes internamente en orden BGR (Azul, Verde, Rojo). Como Tkinter y Pillow esperan RGB, convertimos con `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` al mostrarla en pantalla, y al leer un píxel `img[y, x]` extraemos `(b, g, r)` y lo mostramos como `(r, g, b)`.
- **Previsualización limpia (Doble buffer):** Al arrastrar el ratón (`<B1-Motion>`), dibujamos sobre una copia temporal en memoria (`preview = self.image.copy()`). Solo al soltar el botón (`<ButtonRelease-1>`) se plasma definitivamente sobre `self.image`. Esto evita que la imagen se emborrone con trazos intermedios.
- **Grabación paso a paso:** No grabamos la pantalla de forma continua a 60 FPS (lo que generaría vídeos pesados con tiempos muertos). En su lugar, capturamos un fotograma clave cada vez que se confirma un trazo y lo repetimos ligeramente para que en el MP4 se aprecie la evolución del dibujo de forma fluida y clara.
