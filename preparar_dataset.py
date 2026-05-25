import numpy as np
import os
import re
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
import cv2

# ============================================================
# RUTA DEL DATASET
# ============================================================
dirname = os.path.join(os.getcwd(), 'C:\\IA\\dataset')
imgpath = dirname + os.sep

images      = []
directories = []
dircount    = []
prevRoot    = ''
cant        = 0

print("Leyendo imagenes de:", imgpath)

for root, dirnames, filenames in os.walk(imgpath):
    dirnames.sort()   # forzar orden alfabetico consistente
    filenames.sort()
    for filename in filenames:
        if re.search(r"\.(jpg|jpeg|png|bmp|tiff)$", filename):
            filepath = os.path.join(root, filename)
            try:
                # 1. Leer con cv2 (uint8, sin float64)
                image = cv2.imread(filepath)
                if image is None:
                    raise ValueError("cv2 no pudo leer la imagen")
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            except Exception as e:
                print(f"\n[SKIP] {filepath}: {e}")
                continue

            cant = cant + 1

            # 2. Center crop (cuadrado central)
            h, w = image.shape[:2]
            lado = min(h, w)
            y0   = (h - lado) // 2
            x0   = (w - lado) // 2
            image = image[y0:y0+lado, x0:x0+lado]

            # 3. Resize a 64x64 en uint8 (cv2 no usa float64)
            image = cv2.resize(image, (64, 64), interpolation=cv2.INTER_AREA)

            images.append(image)
            print(f"Leyendo...{cant}", end="\r")

        if prevRoot != root:
            prevRoot = root
            directories.append(root)
            dircount.append(cant)
            cant = 0

dircount.append(cant)
dircount = dircount[1:]
dircount[0] = dircount[0] + 1

print('\nDirectorios leidos:', len(directories))
print("Imagenes en cada directorio:", dircount)
print('Total de imagenes:', sum(dircount))

# ============================================================
# ETIQUETAS
# ============================================================
labels = []
indice = 0
for cantidad in dircount:
    for i in range(cantidad):
        labels.append(indice)
    indice = indice + 1
print("Etiquetas creadas:", len(labels))

animales = []
indice = 0
for directorio in directories:
    name = directorio.split(os.sep)
    print(indice, name[len(name)-1])
    animales.append(name[len(name)-1])
    indice = indice + 1

# ============================================================
# ARRAYS NUMPY
# ============================================================
y = np.array(labels)
X = np.array(images, dtype=np.uint8)

classes  = np.unique(y)
nClasses = len(classes)
print('Numero de clases:', nClasses)
print('Clases:', classes)

# ============================================================
# DIVIDIR
# ============================================================
train_X, test_X, train_Y, test_Y = train_test_split(X, y, test_size=0.2)
print('Entrenamiento:', train_X.shape, train_Y.shape)
print('Prueba:       ', test_X.shape,  test_Y.shape)

plt.figure(figsize=[5, 5])
plt.subplot(121)
plt.imshow(train_X[0])
plt.title("Train: {}".format(animales[train_Y[0]]))
plt.subplot(122)
plt.imshow(test_X[0])
plt.title("Test: {}".format(animales[test_Y[0]]))
plt.show()

# ============================================================
# ONE-HOT ENCODING
# ============================================================
train_Y_one_hot = to_categorical(train_Y)
test_Y_one_hot  = to_categorical(test_Y)
print('Etiqueta original:', train_Y[0])
print('Etiqueta one-hot: ', train_Y_one_hot[0])

train_X, valid_X, train_label, valid_label = train_test_split(
    train_X, train_Y_one_hot, test_size=0.2, random_state=13
)
print(train_X.shape, valid_X.shape, train_label.shape, valid_label.shape)

# ============================================================
# GUARDAR
# ============================================================
output_dir = r'C:\IA\datos'
os.makedirs(output_dir, exist_ok=True)

np.save(os.path.join(output_dir, 'train_X.npy'),        train_X)
np.save(os.path.join(output_dir, 'valid_X.npy'),        valid_X)
np.save(os.path.join(output_dir, 'test_X.npy'),         test_X)
np.save(os.path.join(output_dir, 'train_label.npy'),    train_label)
np.save(os.path.join(output_dir, 'valid_label.npy'),    valid_label)
np.save(os.path.join(output_dir, 'test_Y.npy'),         test_Y)
np.save(os.path.join(output_dir, 'test_Y_one_hot.npy'), test_Y_one_hot)
np.save(os.path.join(output_dir, 'animales.npy'),       np.array(animales))
np.save(os.path.join(output_dir, 'nClasses.npy'),       np.array(nClasses))

print("\nDatos guardados en", output_dir)