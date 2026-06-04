import os
import re
import pickle

import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ruta_base = os.path.dirname(__file__)
ruta_modelo = os.path.join(ruta_base, "modelo_rnn.keras")
ruta_mappings = os.path.join(ruta_base, "tokenizer_mappings.pkl")

with open(ruta_mappings, "rb") as archivo:
    mappings = pickle.load(archivo)

stoi = mappings["stoi"]
itos = mappings["itos"]
VOCAB_SIZE = mappings["vocab_size"]

modelo_completo = tf.keras.models.load_model(ruta_modelo, compile=False)
block_size = modelo_completo.input_shape[1]

embedding_layer = modelo_completo.get_layer("embedding")
rnn_layer = modelo_completo.get_layer("simple_rnn")
time_distributed_layer = modelo_completo.get_layer("time_distributed")

embed_dim = embedding_layer.output_dim
hidden = rnn_layer.units

modelo = tf.keras.Sequential(
    [
        tf.keras.layers.Input(shape=(block_size,), dtype=tf.int64),
        tf.keras.layers.Embedding(VOCAB_SIZE, embed_dim, name="embedding"),
        tf.keras.layers.SimpleRNN(
            hidden,
            activation="tanh",
            return_sequences=False,
            name="simple_rnn",
        ),
        tf.keras.layers.Dense(VOCAB_SIZE, name="dense_salida"),
    ]
)

modelo.get_layer("embedding").set_weights(embedding_layer.get_weights())
modelo.get_layer("simple_rnn").set_weights(rnn_layer.get_weights())
modelo.get_layer("dense_salida").set_weights(time_distributed_layer.layer.get_weights())

del modelo_completo

print(f"Modelo cargado | vocab={VOCAB_SIZE} | block_size={block_size}")

TEMPERATURA = 0.01
TOP_K = 1


@tf.function
def step(x):
    return modelo(x, training=False)


def decodificar(indices):
    return "".join(itos[int(i)] for i in indices)


def extraer_bloque_actual(codigo):
    codigo = codigo.replace("\r\n", "\n")

    patron_firma = re.compile(
        r"(?m)^\s*(int|float|void|double|char)\s+kz_[a-zA-Z0-9_]+\s*\([^;\n]*\)\s*\{?"
    )

    coincidencias = list(patron_firma.finditer(codigo))

    if coincidencias:
        inicio = coincidencias[-1].start()
        return codigo[inicio:].lstrip()

    return codigo.lstrip()


def llaves_balanceadas(texto):
    balance = 0
    comenzo = False

    for caracter in texto:
        if caracter == "{":
            balance += 1
            comenzo = True
        elif caracter == "}":
            balance -= 1

    return comenzo and balance == 0


def muestrear(logits):
    logits = np.asarray(logits, dtype=np.float64)

    if TOP_K == 1:
        return int(np.argmax(logits))

    logits = logits / max(TEMPERATURA, 1e-6)

    if TOP_K > 0:
        indices = np.argpartition(logits, -TOP_K)[-TOP_K:]
        mascara = np.full_like(logits, -np.inf)
        mascara[indices] = logits[indices]
        logits = mascara

    logits = logits - np.max(logits)
    exp = np.exp(logits)
    probs = exp / np.sum(exp)

    return int(np.random.choice(len(probs), p=probs))


def generar(prompt, max_nuevos=350):
    ids = [stoi.get(c, 0) for c in prompt]

    if len(ids) == 0:
        ids = [0]

    for _ in range(max_nuevos):
        contexto = ids[-block_size:]
        x = np.array(contexto, dtype=np.int64)

        if x.shape[0] < block_size:
            padding = np.zeros(block_size - x.shape[0], dtype=np.int64)
            x = np.concatenate([padding, x])

        x = x.reshape(1, block_size)

        logits = step(x).numpy()[0]
        siguiente_id = muestrear(logits)

        ids.append(siguiente_id)

        texto_actual = decodificar(ids)

        if llaves_balanceadas(texto_actual) and texto_actual.rstrip().endswith("}"):
            break

    return decodificar(ids)


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "modelo": "rnn_vanilla_kz",
            "vocab_size": VOCAB_SIZE,
            "block_size": block_size,
        }
    )


@app.route("/autocompletar", methods=["POST"])
def autocompletar():
    datos = request.get_json(force=True)

    codigo = datos.get("codigo", "")
    max_tokens = int(datos.get("max_tokens", 350))

    if codigo.strip() == "":
        return jsonify({"error": "No se envio codigo"}), 400

    prompt_modelo = extraer_bloque_actual(codigo)

    codigo_generado = generar(prompt_modelo, max_nuevos=max_tokens)
    completado = codigo_generado[len(prompt_modelo):]

    return jsonify(
        {
            "codigo_original": codigo,
            "prompt_modelo": prompt_modelo,
            "completado": completado,
            "codigo_completo": codigo + completado,
        }
    )


if __name__ == "__main__":
    print("API lista en http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)