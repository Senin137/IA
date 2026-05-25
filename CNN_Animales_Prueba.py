import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import resize
from skimage.color import rgba2rgb, gray2rgb
from keras.models import load_model

# ============================================================
# CARGAR EL MODELO GUARDADO
# ============================================================
modelo_path = r'C:\IA\animales.keras'
animal_model = load_model(modelo_path)

animales = ['arana', 'ballena', 'chango', 'pajaro', 'rana']

# ============================================================
# ESPECIFICAR LA IMAGEN A PROBAR
# ============================================================
filenames = [r'C:\IA\animales\prueba\chango5.jpg']

# ============================================================
# FUNCIÓN PARA NORMALIZAR CUALQUIER IMAGEN A RGB
# ============================================================
def normalizar_a_rgb(image):
    """Convierte cualquier imagen a RGB con valores float64 en [0, 1]."""

    # 1. Si es float y los valores superan 1.0, normalizar a [0,1]
    if image.dtype in [np.float32, np.float64] and image.max() > 1.0:
        image = image / 255.0

    # 2. Si es uint16 o uint32, bajar a uint8
    if image.dtype in [np.uint16, np.uint32]:
        image = (image / image.max() * 255).astype(np.uint8)

    # 3. Convertir según el número de canales
    if image.ndim == 2:
        # Escala de grises → RGB
        image = gray2rgb(image)

    elif image.ndim == 3:
        canales = image.shape[2]

        if canales == 1:
            # (H, W, 1) → RGB
            image = gray2rgb(image[:, :, 0])

        elif canales == 4:
            # RGBA → RGB (aplana el canal alfa sobre fondo blanco)
            if image.dtype == np.uint8:
                image = image.astype(np.float64) / 255.0
            image = rgba2rgb(image)

        elif canales == 3:
            # Ya es RGB, solo asegurar float [0,1]
            if image.dtype == np.uint8:
                image = image.astype(np.float64) / 255.0

        else:
            raise ValueError(f"Imagen con {canales} canales no soportada.")

    else:
        raise ValueError(f"Forma de imagen no soportada: {image.shape}")

    return image  # float64 en [0.0, 1.0], shape (H, W, 3)

# ============================================================
# PROCESAR IMÁGENES
# ============================================================
images = []
for filepath in filenames:
    image = plt.imread(filepath)          # leer imagen (cualquier formato)
    image = normalizar_a_rgb(image)       # ← conversión universal a RGB

    image_resized = resize(image, (64, 64),
                           anti_aliasing=True,
                           clip=True,           # clip=True porque ya está en [0,1]
                           preserve_range=False)
    images.append(image_resized)

test_X = np.array(images, dtype=np.float32)    # ya normalizado en [0,1]

# ============================================================
# PREDECIR
# ============================================================
predicted_classes = animal_model.predict(test_X)

# ============================================================
# MOSTRAR RESULTADO
# ============================================================
for i, img_tagged in enumerate(predicted_classes):
    clase_idx  = img_tagged.tolist().index(max(img_tagged))
    clase_pred = animales[clase_idx]
    confianza  = max(img_tagged) * 100

    print(f"\nImagen : {filenames[i]}")
    print(f"Animal detectado: {clase_pred.upper()}  ({confianza:.1f}% de confianza)")

    print("\nProbabilidades:")
    for animal, prob in zip(animales, img_tagged):
        barra = "█" * int(prob * 30)
        print(f"  {animal:10s}: {prob*100:5.1f}%  {barra}")

    plt.figure(figsize=(4, 4))
    plt.imshow(plt.imread(filenames[i]))
    plt.title(f"Predicción: {clase_pred}\nConfianza: {confianza:.1f}%", fontsize=12)
    plt.axis('off')
    plt.tight_layout()
    plt.show()