# Práctica 1 — Procesamiento de Imágenes, Audio y Vídeo (PIAV)

Visor de imágenes con inspector de píxel y editor gráfico interactivo, desarrollado en Python con **OpenCV**, **Tkinter**, **Pillow** y **NumPy**.

La aplicación permite cargar una imagen, consultar el valor RGB del píxel bajo el cursor y dibujar primitivas geométricas con el ratón (líneas, rectángulos, círculos, elipses, polilíneas y polígonos), con color RGB, grosor y relleno configurables. Además puede grabar el proceso de dibujo como vídeo.

---

## Enunciado

### Parte obligatoria (5 puntos)

- **1a.** Cargar una imagen y mostrar el valor RGB del píxel sobre el que está el cursor del ratón.
- **1b.** Dibujar con el ratón las siguientes primitivas:
  - Líneas
  - Rectángulos
  - Círculos
  - Especificar el color RGB de las primitivas
  - Definir el grosor de las líneas

### Parte optativa (5 puntos)

- Figuras rellenas, seleccionables desde la interfaz.
- Otras primitivas: polilíneas, polígonos y elipses.
- Guardar el dibujo como un vídeo para ver cómo se realizó paso a paso.
- Aportación propia.

---

## Estado del desarrollo

| Funcionalidad                                   | Tipo              | Estado |
| ----------------------------------------------- | ----------------- | :----: |
| Cargar y visualizar imagen                      | Obligatorio       | ✅ |
| RGB del píxel bajo el cursor                    | Obligatorio       | ✅ |
| Barra de herramientas (forma, color, grosor)    | Base              | ✅ |
| Dibujo con ratón: línea, rectángulo, círculo    | Obligatorio       | ✅ |
| Color RGB y grosor aplicados al dibujo          | Obligatorio       | ✅ |
| Figuras rellenas                                | Optativo          | ⬜ |
| Elipse, polilínea y polígono                    | Optativo          | ⬜ |
| Guardar imagen / restaurar original             | Pulido            | ⬜ |
| Grabación del proceso como vídeo                | Optativo          | ⬜ |
| Inspector de píxel avanzado                     | Aportación propia | ⬜ |
| Deshacer / rehacer                              | Pulido extra      | ⬜ |

---

## Requisitos

- Python **3.12** o superior
- [uv](https://docs.astral.sh/uv/) (recomendado) o `pip`
- Tkinter (incluido con Python en Windows/macOS; en algunas distribuciones Linux hay que instalarlo aparte, p. ej. `sudo apt install python3-tk`)

Dependencias (definidas en `pyproject.toml`):

- `opencv-python`
- `pillow`
- `numpy`

## Instalación

### Con uv (recomendado)

```bash
uv sync
```

### Con pip

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install opencv-python pillow numpy
```

## Ejecución

```bash
uv run main.py
# o, con el entorno virtual activado:
python main.py
```

---

## Uso

1. Pulsa **Abrir imagen** y selecciona un archivo `.png`, `.jpg`, `.jpeg` o `.bmp`.
2. Mueve el cursor sobre la imagen: la etiqueta inferior muestra `RGB: (R, G, B)` del píxel bajo el cursor.
3. En la barra de herramientas elige:
   - **Herramienta:** Línea, Rectángulo, Círculo, Elipse, Polilínea o Polígono.
   - **Color:** valores R, G y B (0–255).
   - **Grosor:** de 1 a 50 píxeles.
   - **Rellenar:** para figuras cerradas (rectángulo, círculo, elipse, polígono).
4. Dibuja sobre la imagen:
   - **Línea / rectángulo / círculo / elipse:** pulsar, arrastrar (se muestra una previsualización) y soltar para confirmar.
   - **Polilínea / polígono:** cada clic añade un vértice; la figura se finaliza con doble clic o con el botón *Finalizar figura*. El polígono se cierra uniendo el último vértice con el primero.
5. Usa **Iniciar / Detener grabación** para exportar el proceso de dibujo como vídeo (`output/proceso_dibujo.mp4`).
6. Usa **Guardar imagen** para exportar el resultado (`output/dibujo_final.png`) o **Restaurar** para volver a la imagen original.

---

## Estructura del proyecto

```
Practica_1/
├── main.py             # Punto de entrada: crea la ventana y lanza DrawingApp
├── app.py              # Clase principal DrawingApp (interfaz y eventos)
├── drawing_tools.py    # Funciones de dibujo de primitivas
├── video_recorder.py   # Grabación del proceso de dibujo como vídeo
├── utils.py            # Conversiones de color y utilidades
├── assets/             # Imágenes de prueba
├── output/             # Imágenes y vídeos generados
├── pyproject.toml      # Metadatos y dependencias
└── README.md
```

---

## Detalles técnicos

### Representación de la imagen

OpenCV carga las imágenes como matrices NumPy de forma `(alto, ancho, 3)` con los canales en orden **BGR**. Por ello:

- Para **mostrar** la imagen en Tkinter se convierte BGR → RGB → `PIL.Image` → `ImageTk.PhotoImage`. La referencia se guarda en `self.tk_image` para que el recolector de basura de Python no la elimine y la imagen no desaparezca de la interfaz.
- Para **leer** un píxel se accede como `imagen[y, x]` (fila, columna) y se obtiene `(b, g, r)`, que se muestra al usuario como `(r, g, b)`.
- Para **dibujar**, el color elegido por el usuario en RGB se convierte a BGR antes de llamar a las funciones de OpenCV (`get_bgr_color()`).
- Antes de leer un píxel se comprueba que `0 ≤ x < ancho` y `0 ≤ y < alto` para evitar accesos fuera de rango.

### Dibujo con el ratón

El dibujo sigue una máquina de estados sencilla basada en eventos de Tkinter:

| Evento              | Acción                                                                 |
| ------------------- | ---------------------------------------------------------------------- |
| `<ButtonPress-1>`   | Guarda el punto inicial.                                               |
| `<B1-Motion>`       | Dibuja la figura sobre una **copia** de la imagen (previsualización).  |
| `<ButtonRelease-1>` | Dibuja la figura definitivamente sobre la imagen real.                 |

La previsualización se hace sobre `self.image.copy()` para no acumular figuras intermedias mientras se arrastra. Tanto la previsualización como el dibujo final usan la misma función (`draw_current_shape`), de modo que ambos resultados siempre coinciden.

### Primitivas

| Primitiva  | Función OpenCV                   | Interpretación de los puntos                                               |
| ---------- | -------------------------------- | -------------------------------------------------------------------------- |
| Línea      | `cv2.line`                       | Punto inicial y punto final.                                               |
| Rectángulo | `cv2.rectangle`                  | Esquinas opuestas.                                                         |
| Círculo    | `cv2.circle`                     | Centro en el punto inicial; radio = distancia euclídea `√((x2−x1)²+(y2−y1)²)`. |
| Elipse     | `cv2.ellipse`                    | Rectángulo delimitador: centro en el punto medio, semiejes = mitad de ancho y alto. |
| Polilínea  | `cv2.polylines(isClosed=False)`  | Lista de vértices añadidos con clics.                                      |
| Polígono   | `cv2.polylines(isClosed=True)` / `cv2.fillPoly` | Lista de vértices; se cierra al finalizar.                  |

Las líneas se dibujan con `cv2.LINE_AA` (antialiasing) para obtener bordes más suaves.

### Figuras rellenas

OpenCV rellena las primitivas cerradas cuando se pasa `thickness=cv2.FILLED` (grosor negativo). Para polígonos se usa `cv2.fillPoly`. La opción se ignora en líneas y polilíneas, que no son figuras cerradas.

### Grabación en vídeo

Mientras la grabación está activa, se captura un *frame* (copia de la imagen) tras cada cambio significativo: frame inicial, cada figura confirmada y cada vértice/finalización de polilíneas y polígonos. Al detener la grabación, los frames se escriben con `cv2.VideoWriter` (códec `mp4v`), repitiendo cada estado varias veces para que el vídeo no avance demasiado rápido. Todos los frames tienen el mismo tamaño que el lienzo.

---

## Aportación propia — Inspector de píxel avanzado

Amplía el requisito obligatorio del RGB con información adicional del píxel bajo el cursor:

- **RGB:** `(R, G, B)`.
- **Hexadecimal:** `#RRGGBB`.
- **HSV:** obtenido con `cv2.cvtColor(..., cv2.COLOR_BGR2HSV)`; separa el matiz de la saturación y el brillo.
- **Luminancia aproximada:** `0.2126·R + 0.7152·G + 0.0722·B`.
- **Lupa:** región de 11×11 píxeles alrededor del cursor (recortada en los bordes) ampliada con `cv2.INTER_NEAREST`, de modo que cada píxel se ve como un bloque sin interpolar.

Como mejora de usabilidad adicional se incluye **deshacer/rehacer** mediante una pila de historial limitada (para acotar el consumo de memoria de guardar copias completas de la imagen).

---

## Plan de pruebas

| ID  | Prueba                    | Resultado esperado                                   |
| --- | ------------------------- | ---------------------------------------------------- |
| T01 | Abrir PNG/JPG             | Se visualiza correctamente.                          |
| T02 | Cancelar "Abrir"          | No ocurre ningún error.                              |
| T03 | Cursor en píxel rojo puro | `RGB = (255, 0, 0)`.                                 |
| T04 | Cursor en los bordes      | No hay `IndexError`.                                 |
| T05 | Dibujar línea             | Aparece con el color y grosor elegidos.              |
| T06 | Dibujar rectángulo        | Previsualización y resultado coinciden.              |
| T07 | Dibujar círculo           | El radio responde a la distancia del arrastre.       |
| T08 | Cambiar RGB               | Todas las herramientas usan el nuevo color.          |
| T09 | Grosor 1 y grosor alto    | Cambio claramente visible.                           |
| T10 | Relleno activado          | Círculo, rectángulo y elipse quedan sólidos.         |
| T11 | Polilínea                 | Se añaden varios segmentos y queda abierta.          |
| T12 | Polígono                  | Se cierra correctamente y puede rellenarse.          |
| T13 | Grabar vídeo              | Archivo reproducible con el proceso.                 |
| T14 | Guardar imagen            | El archivo conserva el dibujo final.                 |
| T15 | Inspector avanzado        | RGB/HEX/HSV/luminancia/lupa se actualizan.           |
| T16 | Deshacer/rehacer          | Revierte/restaura acciones sin corromper la imagen.  |

---

## Autores

- Daniel Rodríguez Alonso
- Pablo Martinez Suarez
