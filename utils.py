import cv2

def apply_filter(img, filter_name):
    """
    Aplica filtros clásicos de procesamiento digital de imágenes con OpenCV.
    (Aportación propia de la práctica: 100% OpenCV, claro y fácil de defender).
    """
    if img is None:
        return None

    if filter_name == "Escala de Grises":
        # Convertimos a grises y devolvemos en 3 canales BGR para poder seguir dibujando en color
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    elif filter_name == "Desenfoque (Blur)":
        # Filtro Gaussiano para suavizar la imagen y reducir ruido
        return cv2.GaussianBlur(img, (9, 9), 0)

    elif filter_name == "Bordes (Canny)":
        # Detector de bordes Canny; se convierte a 3 canales para visualización uniforme
        edges = cv2.Canny(img, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    elif filter_name == "Invertir Colores":
        # Negativo fotográfico invirtiendo los bits de cada píxel
        return cv2.bitwise_not(img)

    return img.copy()
