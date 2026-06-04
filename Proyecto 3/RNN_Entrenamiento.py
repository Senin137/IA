import os
import re
import glob
import pickle

import numpy as np
import tensorflow as tf

tf.keras.utils.set_random_seed(42)

ruta_base = os.path.dirname(__file__)
ruta_dataset = os.path.join(ruta_base, "corpus_codigo.txt")
ruta_mappings = os.path.join(ruta_base, "tokenizer_mappings.pkl")
ruta_modelo = os.path.join(ruta_base, "modelo_rnn.keras")

with open(ruta_dataset, "r", encoding="utf-8") as archivo:
    CORPUS = archivo.read().replace("\r\n", "\n").strip() + "\n\n"

funciones = re.findall(
    r"^\s*(int|float|void|double|char)\s+kz_[a-zA-Z0-9_]+\s*\(",
    CORPUS,
    flags=re.MULTILINE,
)

print("Funciones detectadas:", len(funciones))

if len(funciones) < 60:
    raise ValueError("El dataset debe tener por lo menos 60 funciones en C.")

chars = sorted(set(CORPUS))
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}
VOCAB_SIZE = len(chars)

with open(ruta_mappings, "wb") as archivo:
    pickle.dump(
        {
            "stoi": stoi,
            "itos": itos,
            "vocab_size": VOCAB_SIZE,
        },
        archivo,
    )

def encode(texto):
    return [stoi[c] for c in texto]

def decode(indices):
    return "".join(itos[i] for i in indices)

SEQ = np.array(encode(CORPUS), dtype=np.int64)

print("VOCAB_SIZE:", VOCAB_SIZE)
print("Caracteres en corpus:", len(CORPUS))

block_size = 128

X_rows = []
Y_rows = []

for i in range(0, len(SEQ) - block_size):
    X_rows.append(SEQ[i : i + block_size])
    Y_rows.append(SEQ[i + 1 : i + 1 + block_size])

X = np.stack(X_rows)
Y = np.stack(Y_rows)

print("Forma de X:", X.shape)
print("Forma de Y:", Y.shape)

embed_dim = 96
hidden = 192

model = tf.keras.Sequential(
    [
        tf.keras.layers.Input(shape=(block_size,)),
        tf.keras.layers.Embedding(VOCAB_SIZE, embed_dim, name="embedding"),
        tf.keras.layers.SimpleRNN(
            hidden,
            activation="tanh",
            return_sequences=True,
            name="simple_rnn",
        ),
        tf.keras.layers.TimeDistributed(
            tf.keras.layers.Dense(VOCAB_SIZE, name="dense_salida"),
            name="time_distributed",
        ),
    ]
)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
)

model.summary()

epochs = 220
batch_size = 32

checkpoint_path = os.path.join(ruta_base, "checkpoint_epoch_{epoch:03d}.h5")

callbacks = [
    tf.keras.callbacks.ModelCheckpoint(
        checkpoint_path,
        save_best_only=False,
        save_freq="epoch",
        verbose=0,
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="loss",
        factor=0.5,
        patience=8,
        min_lr=0.00001,
        verbose=1,
    ),
    tf.keras.callbacks.EarlyStopping(
        monitor="loss",
        patience=25,
        min_delta=0.0002,
        verbose=1,
    ),
]

history = model.fit(
    X,
    Y,
    epochs=epochs,
    batch_size=batch_size,
    callbacks=callbacks,
    verbose=2,
)

print("Epocas entrenadas:", len(history.history["loss"]))
print("Perdida inicial:", round(float(history.history["loss"][0]), 4))
print("Perdida final:", round(float(history.history["loss"][-1]), 4))

model.save(ruta_modelo)
print("Modelo guardado en:", ruta_modelo)

for archivo in glob.glob(os.path.join(ruta_base, "checkpoint_epoch_*.h5")):
    os.remove(archivo)

print("Checkpoints temporales eliminados")

def muestrear(logits, temperatura=0.01, top_k=1):
    if top_k == 1:
        return int(np.argmax(logits))

    z = logits / max(temperatura, 1e-6)
    z = z - z.max()

    if top_k > 0:
        indices = np.argpartition(z, -top_k)[-top_k:]
        mask = np.full_like(z, -np.inf)
        mask[indices] = z[indices]
        z = mask

    e = np.exp(z)
    p = e / e.sum()

    return int(np.random.choice(len(p), p=p))

def llaves_balanceadas(texto):
    balance = 0
    comenzo_funcion = False

    for caracter in texto:
        if caracter == "{":
            balance += 1
            comenzo_funcion = True
        elif caracter == "}":
            balance -= 1

    return comenzo_funcion and balance == 0

def completar(prompt, max_nuevos=500):
    ids = [stoi.get(c, 0) for c in prompt]

    if len(ids) == 0:
        ids = [0]

    for _ in range(max_nuevos):
        contexto = ids[-block_size:]
        x = np.array(contexto, dtype=np.int64)

        if x.shape[0] < block_size:
            padding = np.full(block_size - x.shape[0], ids[0], dtype=np.int64)
            x = np.concatenate([padding, x])

        x = x.reshape(1, block_size)

        logits = model(x, training=False).numpy()[0, -1, :]
        siguiente_id = muestrear(logits)

        ids.append(siguiente_id)

        texto_actual = decode(ids)

        if llaves_balanceadas(texto_actual) and texto_actual.rstrip().endswith("}"):
            break

    return decode(ids)

print("\n--- Prueba 1: es par ---")
print(completar("int kz_es_par(int numero) {", max_nuevos=300))

print("\n--- Prueba 2: sumar arreglo ---")
print(completar("int kz_sumar_arreglo(int arreglo[], int tamanio) {", max_nuevos=400))

print("\n--- Prueba 3: longitud cadena ---")
print(completar("int kz_longitud_cadena(char cadena[]) {", max_nuevos=400))