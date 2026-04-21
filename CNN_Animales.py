import os
import re
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, ConfusionMatrixDisplay, confusion_matrix

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ──────────────────────────────────────────────
#  CONFIGURACIÓN
# ──────────────────────────────────────────────
DATASET_DIR = "./dataset"
MODEL_PATH  = "./modelo_animales_transfer.keras"

IMG_SIZE    = (224, 224)   # MobileNetV2 fue entrenado con 224x224 — no cambiar
IMG_SHAPE   = (224, 224, 3)

BATCH_SIZE  = 16           # Pequeño porque el dataset es pequeño
EPOCHS_HEAD = 15           # Fase 1: solo entrenar la cabeza nueva
EPOCHS_FINE = 25           # Fase 2: fine-tuning de las últimas capas base
INIT_LR     = 1e-3         # LR para fase 1
FINE_LR     = 1e-5         # LR más pequeño para fine-tuning

EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

# ──────────────────────────────────────────────
#  1. CARGA DE IMÁGENES
# ──────────────────────────────────────────────
images, labels, clases = [], [], []

print(f" Leyendo imágenes desde: {DATASET_DIR}\n")

for indice, nombre_clase in enumerate(sorted(os.listdir(DATASET_DIR))):
    carpeta = os.path.join(DATASET_DIR, nombre_clase)
    if not os.path.isdir(carpeta):
        continue

    clases.append(nombre_clase)
    count = 0

    for filename in os.listdir(carpeta):
        if os.path.splitext(filename)[1].lower() not in EXTENSIONES:
            continue
        filepath = os.path.join(carpeta, filename)
        img = tf.io.read_file(filepath)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, IMG_SIZE)
        images.append(img.numpy().astype(np.uint8))
        labels.append(indice)
        count += 1

    print(f"  [{indice}] {nombre_clase}: {count} imágenes")

nClases = len(clases)
print(f"\n✅ Total: {len(images)} imágenes | {nClases} clases: {clases}\n")

# ──────────────────────────────────────────────
#  2. PREPROCESAMIENTO
# ──────────────────────────────────────────────
# MobileNetV2 espera píxeles en [-1, 1], no [0, 1]
X = tf.keras.applications.mobilenet_v2.preprocess_input(
    np.array(images, dtype=np.float32)
)
y = np.array(labels)

# Split estratificado (respeta la proporción de clases)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, stratify=y, random_state=42
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train, test_size=0.15, stratify=y_train, random_state=42
)

print(f"Train: {X_train.shape[0]} | Val: {X_val.shape[0]} | Test: {X_test.shape[0]}")

y_train_oh = to_categorical(y_train, nClases)
y_val_oh   = to_categorical(y_val,   nClases)
y_test_oh  = to_categorical(y_test,  nClases)

# ──────────────────────────────────────────────
#  3. DATA AUGMENTATION  (muy importante con pocos datos)
# ──────────────────────────────────────────────
datagen = ImageDataGenerator(
    rotation_range=30,
    width_shift_range=0.15,
    height_shift_range=0.15,
    horizontal_flip=True,
    vertical_flip=False,
    zoom_range=0.2,
    brightness_range=[0.7, 1.3],
    shear_range=10,
    fill_mode='reflect'
)
datagen.fit(X_train)

# ──────────────────────────────────────────────
#  4. MODELO — Transfer Learning con MobileNetV2
# ──────────────────────────────────────────────

# Cargar MobileNetV2 SIN la capa de clasificación final
# include_top=False → quita la capa Dense de las 1000 clases de ImageNet
base_model = MobileNetV2(
    input_shape=IMG_SHAPE,
    include_top=False,
    weights='imagenet'
)

# ── FASE 1: congelar toda la base, solo entrenar la cabeza ──
base_model.trainable = False

inputs  = tf.keras.Input(shape=IMG_SHAPE)
x       = base_model(inputs, training=False)
x       = layers.GlobalAveragePooling2D()(x)
x       = layers.Dense(128, activation='relu')(x)
x       = layers.Dropout(0.4)(x)
outputs = layers.Dense(nClases, activation='softmax')(x)

model = models.Model(inputs, outputs)
model.summary()

callbacks_fase1 = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
]

print("\n FASE 1: Entrenando solo la cabeza del modelo...\n")
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=INIT_LR),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history1 = model.fit(
    datagen.flow(X_train, y_train_oh, batch_size=BATCH_SIZE),
    epochs=EPOCHS_HEAD,
    validation_data=(X_val, y_val_oh),
    callbacks=callbacks_fase1,
    verbose=1
)

# ── FASE 2: descongelar las últimas capas para fine-tuning ──
print("\n🟠 FASE 2: Fine-tuning de las últimas capas de MobileNetV2...\n")

base_model.trainable = True

# Congelar todo excepto las últimas 30 capas
for layer in base_model.layers[:-30]:
    layer.trainable = False

# LR mucho más pequeño para no destruir los pesos pre-entrenados
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=FINE_LR),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_fase2 = [
    EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, verbose=1)
]

history2 = model.fit(
    datagen.flow(X_train, y_train_oh, batch_size=BATCH_SIZE),
    epochs=EPOCHS_FINE,
    validation_data=(X_val, y_val_oh),
    callbacks=callbacks_fase2,
    verbose=1
)

model.save(MODEL_PATH)
print(f"\n💾 Modelo guardado en: {MODEL_PATH}")

# ──────────────────────────────────────────────
#  5. EVALUACIÓN
# ──────────────────────────────────────────────
test_loss, test_acc = model.evaluate(X_test, y_test_oh, verbose=0)
print(f"\n🎯 Test accuracy : {test_acc:.4f}")
print(f"📉 Test loss     : {test_loss:.4f}")

predicted_probs   = model.predict(X_test)
predicted_classes = np.argmax(predicted_probs, axis=1)

print("\n📋 Reporte de clasificación:")
print(classification_report(y_test, predicted_classes, target_names=clases))

# ──────────────────────────────────────────────
#  6. GRÁFICAS
# ──────────────────────────────────────────────
def unir_historiales(h1, h2, key):
    return h1.history[key] + h2.history[key]

epochs_total = range(len(unir_historiales(history1, history2, 'accuracy')))
fase1_len    = len(history1.history['accuracy'])

fig, axes = plt.subplots(1, 2, figsize=(14, 4))

for ax, metric, title in zip(axes, ['accuracy', 'loss'], ['Accuracy', 'Loss']):
    train_vals = unir_historiales(history1, history2, metric)
    val_vals   = unir_historiales(history1, history2, f'val_{metric}')
    ax.plot(epochs_total, train_vals, label='Train')
    ax.plot(epochs_total, val_vals,   label='Validación')
    ax.axvline(x=fase1_len - 1, color='gray', linestyle='--', label='Inicio fine-tuning')
    ax.set_title(f'{title} por epoch')
    ax.set_xlabel('Epoch')
    ax.legend()

plt.tight_layout()
plt.savefig("./curvas_entrenamiento.png", dpi=150)
plt.show()

# Matriz de confusión
cm = confusion_matrix(y_test, predicted_classes)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clases)
disp.plot(xticks_rotation=45, cmap='Blues')
plt.title("Matriz de confusión")
plt.tight_layout()
plt.savefig("./confusion_matrix.png", dpi=150)
plt.show()

# ──────────────────────────────────────────────
#  7. VISTA PREVIA de predicciones
# ──────────────────────────────────────────────
# Desnormalizar para visualizar
X_test_vis = ((X_test + 1) / 2.0).clip(0, 1)

def mostrar_predicciones(indices, titulo):
    if len(indices) == 0:
        print(f"(Sin casos para: {titulo})")
        return
    plt.figure(figsize=(12, 4))
    plt.suptitle(titulo, fontsize=13)
    for i, idx in enumerate(indices[:9]):
        plt.subplot(3, 3, i + 1)
        plt.imshow(X_test_vis[idx])
        pred  = clases[predicted_classes[idx]]
        real  = clases[y_test[idx]]
        color = 'green' if pred == real else 'red'
        plt.title(f"Pred: {pred}\nReal: {real}", color=color, fontsize=8)
        plt.axis('off')
    plt.tight_layout()
    plt.show()

correctos   = np.where(predicted_classes == y_test)[0]
incorrectos = np.where(predicted_classes != y_test)[0]

print(f"\n Correctos  : {len(correctos)}")
print(f" Incorrectos: {len(incorrectos)}")

mostrar_predicciones(correctos,   " Predicciones correctas")
mostrar_predicciones(incorrectos, " Predicciones incorrectas")