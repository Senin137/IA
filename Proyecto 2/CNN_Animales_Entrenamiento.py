import numpy as np
import os
import matplotlib.pyplot as plt
import keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.layers import LeakyReLU

# ============================================================
# CARGAR DATOS Y METADATOS
# ============================================================
data_dir = r'C:\IA\datos'

train_X     = np.load(os.path.join(data_dir, 'train_X.npy'))
valid_X     = np.load(os.path.join(data_dir, 'valid_X.npy'))
test_X      = np.load(os.path.join(data_dir, 'test_X.npy'))
train_label = np.load(os.path.join(data_dir, 'train_label.npy'))
valid_label = np.load(os.path.join(data_dir, 'valid_label.npy'))
test_Y_one_hot = np.load(os.path.join(data_dir, 'test_Y_one_hot.npy'))
test_Y      = np.load(os.path.join(data_dir, 'test_Y.npy'))

animales  = np.load(os.path.join(data_dir, 'animales.npy'), allow_pickle=True)
nClasses  = int(np.load(os.path.join(data_dir, 'nClasses.npy')))

print("Clases:", list(animales))
print(train_X.shape, valid_X.shape, train_label.shape, valid_label.shape)

# ============================================================
# PARAMETROS
# ============================================================
INIT_LR    = 1e-3
epochs     = 50
batch_size = 32

# ============================================================
# PIPELINES tf.data
# Normaliza /255 batch a batch sin crear arrays float32 en RAM
# ============================================================
def augmentar(imagen, etiqueta):
    imagen = tf.cast(imagen, tf.float32) / 255.
    imagen = tf.image.random_flip_left_right(imagen)
    imagen = tf.image.random_brightness(imagen, 0.1)
    imagen = tf.image.random_contrast(imagen, 0.9, 1.1)
    return imagen, etiqueta

def solo_normalizar(imagen, etiqueta):
    imagen = tf.cast(imagen, tf.float32) / 255.
    return imagen, etiqueta

ds_train = (tf.data.Dataset.from_tensor_slices((train_X, train_label))
            .shuffle(2000)
            .map(augmentar, num_parallel_calls=tf.data.AUTOTUNE)
            .batch(batch_size)
            .prefetch(tf.data.AUTOTUNE))

ds_valid = (tf.data.Dataset.from_tensor_slices((valid_X, valid_label))
            .map(solo_normalizar, num_parallel_calls=tf.data.AUTOTUNE)
            .batch(batch_size)
            .prefetch(tf.data.AUTOTUNE))

ds_test = (tf.data.Dataset.from_tensor_slices((test_X, test_Y_one_hot))
           .map(solo_normalizar, num_parallel_calls=tf.data.AUTOTUNE)
           .batch(batch_size))

# ============================================================
# MODELO CNN
# ============================================================
animal_model = Sequential()
animal_model.add(tf.keras.Input(shape=(64, 64, 3)))

# Bloque 1: detecta bordes y texturas basicas
animal_model.add(Conv2D(32, kernel_size=(3, 3), activation='linear', padding='same'))
animal_model.add(LeakyReLU(negative_slope=0.1))
animal_model.add(MaxPooling2D((2, 2), padding='same'))

# Bloque 2: detecta formas mas complejas
animal_model.add(Conv2D(64, (3, 3), activation='linear', padding='same'))
animal_model.add(LeakyReLU(negative_slope=0.1))
animal_model.add(MaxPooling2D((2, 2), padding='same'))

# Bloque 3: detecta patrones de alto nivel (pelaje, escamas, plumas)
animal_model.add(Conv2D(128, (3, 3), activation='linear', padding='same'))
animal_model.add(LeakyReLU(negative_slope=0.1))
animal_model.add(MaxPooling2D((2, 2), padding='same'))
animal_model.add(Dropout(0.3))   # solo un dropout antes de la cabeza

# GlobalAveragePooling en lugar de Flatten:
# promedia cada mapa de activacion completo -> ignora DONDE esta el patron
# y se enfoca en SI existe el patron (ej: textura de plumas, escamas, pelo)
animal_model.add(tf.keras.layers.GlobalAveragePooling2D())
animal_model.add(Dense(128, activation='linear'))
animal_model.add(LeakyReLU(negative_slope=0.1))
animal_model.add(Dropout(0.5))
animal_model.add(Dense(nClasses, activation='softmax'))

animal_model.summary()

# ============================================================
# COMPILAR
# ============================================================
animal_model.compile(
    loss=keras.losses.categorical_crossentropy,
    optimizer=tf.keras.optimizers.Adam(learning_rate=INIT_LR),
    metrics=['accuracy']
)

# ============================================================
# ENTRENAR (con pesos de clase para balancear el dataset)
# ============================================================
animal_train = animal_model.fit(
    ds_train,
    epochs=epochs,
    verbose=1,
    validation_data=ds_valid
)

# ============================================================
# GUARDAR MODELO
# ============================================================
model_path = r'C:\IA\animales.keras'
animal_model.save(model_path)
print("Modelo guardado en:", model_path)

# ============================================================
# EVALUAR
# ============================================================
test_eval = animal_model.evaluate(ds_test, verbose=1)
print('Test loss:    ', test_eval[0])
print('Test accuracy:', test_eval[1])

# ============================================================
# GRAFICAS
# ============================================================
accuracy     = animal_train.history['accuracy']
val_accuracy = animal_train.history['val_accuracy']
loss         = animal_train.history['loss']
val_loss     = animal_train.history['val_loss']
eps          = range(len(accuracy))

plt.plot(eps, accuracy,     'bo', label='Training accuracy')
plt.plot(eps, val_accuracy, 'b',  label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()
plt.plot(eps, loss,     'bo', label='Training loss')
plt.plot(eps, val_loss, 'b',  label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()

# ============================================================
# PREDICCIONES SOBRE TEST
# ============================================================
ds_test_pred = (tf.data.Dataset.from_tensor_slices(test_X)
                .map(lambda x: tf.cast(x, tf.float32) / 255.)
                .batch(batch_size))

predicted_classes2 = animal_model.predict(ds_test_pred)

predicted_classes = []
for pred in predicted_classes2:
    predicted_classes.append(pred.tolist().index(max(pred)))
predicted_classes = np.array(predicted_classes)

# Mostrar correctas
correct = np.where(predicted_classes == test_Y)[0]
print("Found %d correct labels" % len(correct))
for i, c in enumerate(correct[0:9]):
    plt.subplot(3, 3, i + 1)
    plt.imshow(test_X[c])
    plt.title("{}, {}".format(animales[predicted_classes[c]], animales[test_Y[c]]))
    plt.tight_layout()
plt.show()

# Mostrar incorrectas
incorrect = np.where(predicted_classes != test_Y)[0]
print("Found %d incorrect labels" % len(incorrect))
for i, c in enumerate(incorrect[0:9]):
    plt.subplot(3, 3, i + 1)
    plt.imshow(test_X[c])
    plt.title("{}, {}".format(animales[predicted_classes[c]], animales[test_Y[c]]))
    plt.tight_layout()
plt.show()

from sklearn.metrics import classification_report
target_names = animales
print(classification_report(test_Y, predicted_classes, target_names=target_names))

print("\nEntrenamiento completo!")