import cv2
import os
import argparse
from pathlib import Path


def extraer_frames(
    ruta_video: str,
    carpeta_salida: str,
    intervalo_frames: int = 30,
    escala: float = 0.5,
    calidad_jpeg: int = 70,
    max_frames: int = None,
    etiqueta: str = "frame",
):
    """
    Extrae frames de un video y los guarda con calidad reducida.

    Args:
        ruta_video       : Ruta al archivo de video (.mp4, .avi, etc.)
        carpeta_salida   : Carpeta donde se guardarán los frames
        intervalo_frames : Extraer 1 frame cada N frames  (default: 30 ≈ 1 seg en 30fps)
        escala           : Factor de escala de la imagen (0.5 = mitad del tamaño original)
        calidad_jpeg     : Calidad JPEG del 1 al 100 (menor = más comprimido)
        max_frames       : Límite máximo de frames a extraer (None = sin límite)
        etiqueta         : Prefijo del nombre de archivo
    """

    # --- Validaciones ---
    if not os.path.exists(ruta_video):
        raise FileNotFoundError(f"No se encontró el video: {ruta_video}")

    Path(carpeta_salida).mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        raise IOError(f"No se pudo abrir el video: {ruta_video}")

    # Info del video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duracion_seg = total_frames / fps if fps > 0 else 0

    print(f"\n{'='*55}")
    print(f"  VIDEO : {os.path.basename(ruta_video)}")
    print(f"  Resolución original : {ancho}x{alto}")
    print(f"  FPS                 : {fps:.1f}")
    print(f"  Duración            : {duracion_seg:.1f}s  ({total_frames} frames)")
    print(f"  Resolución salida   : {int(ancho*escala)}x{int(alto*escala)}")
    print(f"  Calidad JPEG        : {calidad_jpeg}%")
    print(f"  Intervalo           : cada {intervalo_frames} frames")
    print(f"{'='*55}\n")

    frames_guardados = 0
    frame_actual = 0

    parametros_jpeg = [cv2.IMWRITE_JPEG_QUALITY, calidad_jpeg]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Extraer solo los frames que correspondan al intervalo
        if frame_actual % intervalo_frames == 0:

            # Redimensionar para reducir tamaño
            if escala != 1.0:
                nuevo_ancho = int(frame.shape[1] * escala)
                nuevo_alto = int(frame.shape[0] * escala)
                frame = cv2.resize(
                    frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA
                )

            # Nombre del archivo: etiqueta_0001.jpg
            nombre_archivo = f"{etiqueta}_{frames_guardados:04d}.jpg"
            ruta_salida = os.path.join(carpeta_salida, nombre_archivo)

            cv2.imwrite(ruta_salida, frame, parametros_jpeg)
            frames_guardados += 1

            # Progreso en consola
            porcentaje = (frame_actual / total_frames) * 100
            print(
                f"\r  Progreso: {porcentaje:5.1f}%  |  Frames guardados: {frames_guardados}",
                end="",
            )

            # Límite opcional
            if max_frames and frames_guardados >= max_frames:
                print(f"\n  Límite de {max_frames} frames alcanzado.")
                break

        frame_actual += 1

    cap.release()

    print(f"\n\n Extracción completa.")
    print(f"   Frames guardados : {frames_guardados}")
    print(f"   Carpeta de salida: {os.path.abspath(carpeta_salida)}\n")

    return frames_guardados


def procesar_multiples_videos(configuracion: list):
    """
    Procesa varios videos de una vez, útil para múltiples clases de animales.

    Args:
        configuracion: Lista de dicts con claves:
                       'video', 'salida', 'etiqueta' (y opcionales del resto)

    Ejemplo:
        configuracion = [
            {"video": "perro.mp4",  "salida": "./dataset/perro",  "etiqueta": "perro"},
            {"video": "gato.mp4",   "salida": "./dataset/gato",   "etiqueta": "gato"},
            {"video": "pajaro.mp4", "salida": "./dataset/pajaro", "etiqueta": "pajaro"},
        ]
    """
    total_general = 0
    for item in configuracion:
        print(f"\n Procesando clase: {item.get('etiqueta', 'animal')}")
        n = extraer_frames(
            ruta_video=item["video"],
            carpeta_salida=item["salida"],
            intervalo_frames=item.get("intervalo_frames", 30),
            escala=item.get("escala", 0.5),
            calidad_jpeg=item.get("calidad_jpeg", 70),
            max_frames=item.get("max_frames", None),
            etiqueta=item.get("etiqueta", "frame"),
        )
        total_general += n

    print(f"\n🏁 Proceso finalizado. Total de imágenes generadas: {total_general}")


# ──────────────────────────────────────────────
#  Ejecución desde línea de comandos
# ──────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrae frames de video para datasets CNN de clasificación de animales."
    )
    parser.add_argument("--video", required=True, help="Ruta al archivo de video")
    parser.add_argument(
        "--output", required=True, help="Carpeta de salida para los frames"
    )
    parser.add_argument(
        "--etiqueta", default="frame", help="Prefijo/nombre de clase (ej: perro)"
    )
    parser.add_argument(
        "--intervalo",
        type=int,
        default=30,
        help="Extraer 1 frame cada N frames (default: 30)",
    )
    parser.add_argument(
        "--escala",
        type=float,
        default=0.5,
        help="Factor de escala 0.1-1.0 (default: 0.5)",
    )
    parser.add_argument(
        "--calidad", type=int, default=70, help="Calidad JPEG 1-100 (default: 70)"
    )
    parser.add_argument(
        "--max", type=int, default=None, help="Máximo de frames a extraer"
    )

    args = parser.parse_args()

    extraer_frames(
        ruta_video=args.video,
        carpeta_salida=args.output,
        intervalo_frames=args.intervalo,
        escala=args.escala,
        calidad_jpeg=args.calidad,
        max_frames=args.max,
        etiqueta=args.etiqueta,
    )
