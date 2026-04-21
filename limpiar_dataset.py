import os
import cv2
import numpy as np
from pathlib import Path

# ──────────────────────────────────────────────
#  CONFIGURACIÓN
# ──────────────────────────────────────────────
INPUT_DIR  = "./dataset/ballena"
OUTPUT_DIR = "./dataset/ballena_limpia"

BLUR_THRESHOLD      = 100    # Varianza del Laplaciano; menor = más borroso
DUPLICATE_THRESHOLD = 5      # Diferencia media de píxeles; menor = más estricto
OUTPUT_SIZE         = (224, 224)   # Tamaño de salida estándar (None para no redimensionar)
EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
#  FUNCIONES
# ──────────────────────────────────────────────

def es_borrosa(img: np.ndarray) -> tuple[bool, float]:
    """Detecta imágenes borrosas con la varianza del Laplaciano."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score < BLUR_THRESHOLD, round(score, 2)


def hash_perceptual(img: np.ndarray, size: int = 16) -> np.ndarray:
    """
    Calcula un hash perceptual (pHash) de la imagen.
    Comparar hashes es O(1) en memoria y mucho más rápido que absdiff
    para detectar duplicados contra *todas* las imágenes guardadas.
    """
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    dct   = cv2.dct(np.float32(small))
    dct_low = dct[:8, :8]          # Solo las frecuencias bajas
    media = dct_low.mean()
    return (dct_low > media).flatten()


def es_duplicado(hash_nuevo: np.ndarray, hashes_guardados: list[np.ndarray]) -> bool:
    """
    Compara el hash con TODOS los guardados (no solo el anterior).
    Usa distancia de Hamming normalizada como métrica de similitud.
    """
    for h in hashes_guardados:
        distancia = np.count_nonzero(hash_nuevo != h) / len(h)
        if distancia < (DUPLICATE_THRESHOLD / 100):
            return True
    return False


def tiene_contenido(img: np.ndarray, umbral_varianza: float = 20.0) -> bool:
    """Descarta imágenes casi completamente en blanco o negro."""
    return img.var() > umbral_varianza


# ──────────────────────────────────────────────
#  PIPELINE PRINCIPAL
# ──────────────────────────────────────────────

archivos = sorted([
    f for f in os.listdir(INPUT_DIR)
    if Path(f).suffix.lower() in EXTENSIONES_VALIDAS
])

total           = len(archivos)
guardadas       = 0
eliminadas_blur = 0
eliminadas_dup  = 0
eliminadas_vacias = 0
errores         = 0

hashes_guardados: list[np.ndarray] = []

print(f"Procesando {total} imágenes en '{INPUT_DIR}'...\n")

for i, nombre in enumerate(archivos, 1):
    ruta = os.path.join(INPUT_DIR, nombre)
    img  = cv2.imread(ruta)

    # Imagen ilegible
    if img is None:
        print(f"   [{i}/{total}] No se pudo leer: {nombre}")
        errores += 1
        continue

    # 1. Descartar imágenes vacías (blanco/negro uniforme)
    if not tiene_contenido(img):
        eliminadas_vacias += 1
        continue

    # 2. Descartar borrosas
    borrosa, score = es_borrosa(img)
    if borrosa:
        eliminadas_blur += 1
        continue

    # 3. Descartar duplicados contra todas las imágenes guardadas
    h = hash_perceptual(img)
    if es_duplicado(h, hashes_guardados):
        eliminadas_dup += 1
        continue

    # 4. Redimensionar si se especifica OUTPUT_SIZE
    if OUTPUT_SIZE is not None:
        img = cv2.resize(img, OUTPUT_SIZE, interpolation=cv2.INTER_AREA)

    # Guardar imagen limpia
    ruta_out = os.path.join(OUTPUT_DIR, nombre)
    cv2.imwrite(ruta_out, img)
    hashes_guardados.append(h)
    guardadas += 1

# ──────────────────────────────────────────────
#  REPORTE FINAL
# ──────────────────────────────────────────────

eliminadas = eliminadas_blur + eliminadas_dup + eliminadas_vacias
pct = lambda n: f"{n / total * 100:.1f}%" if total else "0%"

print("━" * 40)
print("📊  RESULTADO FINAL")
print("━" * 40)
print(f"  Total analizadas  : {total}")
print(f"   Guardadas       : {guardadas} ({pct(guardadas)})")
print(f"   Borrosas        : {eliminadas_blur} ({pct(eliminadas_blur)})")
print(f"   Duplicadas      : {eliminadas_dup} ({pct(eliminadas_dup)})")
print(f"   Vacías/uniformes: {eliminadas_vacias} ({pct(eliminadas_vacias)})")
print(f"    Errores lectura : {errores}")
print("━" * 40)
print(f"  Dataset limpio en : {OUTPUT_DIR}")
print("━" * 40)