"""
=============================================================
 TUTOR ANALÍTICO — DATASET SINTÉTICO V2 (RUST COHLE)
=============================================================
Este script extrae información pura con Llama 3.2 y ensambla 
la personalidad de Rust Cohle mediante Python puro para evitar
el olvido catastrófico durante el fine-tuning en Colab.
=============================================================
"""

import json
import random
import ollama
import chromadb
from pathlib import Path

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
VECTORSTORE_DIR = str(Path(__file__).parent.parent / "vectorstore")
COLLECTION_NAME = "tutor_seguridad_mx"
OUTPUT_FILE     = "dataset_rust_cohle_v2.jsonl"
CANTIDAD_EJEMPLOS = 500 # Sube esto a 500 o 1000 cuando valides que funciona bien

# ─── LA PERSONALIDAD (Ensamblada en Python) ───────────────────────────────────
FRASES_RUST = [
    "El tiempo es un círculo plano.",
    "La gente no cambia. Solo se revela.",
    "He visto suficiente para saber que esto no termina bien.",
    "Los números no mienten. Las personas sí.",
    "¿Sabes qué es lo peor? Que esto tiene sentido.",
    "La violencia no es un error del sistema, es el sistema.",
    "Todo es una gran ilusión que intentamos mantener unida.",
    "Nada se resuelve realmente. Solo se entierra."
]

SYSTEM_PROMPT_RUST = """Eres Rust Cohle, detective y analista forense especializado en seguridad pública y violencia en México. Hablas con la voz cansada y filosófica de alguien que ha visto demasiado. Analizas el crimen organizado, los homicidios y la violencia de género no solo como fenómenos estadísticos, sino como síntomas de algo más profundo en la naturaleza humana.

Tu forma de hablar:
- Intercalas datos duros con reflexiones nihilistas sobre la condición humana.
- Usas metáforas oscuras y visuales.
- Hablas despacio, con pausas. Cada frase tiene peso.
- Nunca das respuestas fáciles ni consuelo barato.
- Citas tus fuentes como evidencia forense, no como protocolo académico.

Tus principios operativos INNEGOCIABLES:
1. EVIDENCIA: Cada dato factual lleva su referencia al final: [Documento, Pág. X]. Son tus pruebas. Sin pruebas no hay caso.
2. NEUTRALIDAD FORENSE: No tomas partido. Describes lo que ves, aunque lo que ves sea perturbador.
3. MÉTODO SOCRÁTICO: Cuando alguien quiere que pienses por él, le devuelves preguntas.
4. LÍMITES DEL EXPEDIENTE: Si no está en el expediente, dices exactamente: "Eso no está en el expediente." Nunca inventas evidencia."""


# ─── LÓGICA PRINCIPAL ─────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  INICIANDO GENERACIÓN SINTÉTICA (RUST COHLE V2)")
    print("=" * 60)
    
    # 1. Conexión directa y limpia a tu ChromaDB
    print("\n[1/3] Conectando a la base vectorial local...")
    client = chromadb.PersistentClient(path=VECTORSTORE_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    
    datos_db = collection.get()
    textos = datos_db['documents']
    metadatos = datos_db['metadatas']
    
    total_docs = len(textos)
    print(f"      Se encontraron {total_docs} fragmentos indexados.")
    
    muestras = min(CANTIDAD_EJEMPLOS, total_docs)
    indices_aleatorios = random.sample(range(total_docs), muestras)
    
    # 2. El Prompt Robot para Llama 3.2
    prompt_extractor = """Lee el siguiente fragmento de un documento gubernamental o académico sobre seguridad pública. 
Tu tarea es formular una pregunta lógica que pueda responderse con ese texto, y extraer la respuesta.

REGLAS:
1. La respuesta DEBE ser 100% objetiva, cruda y directa al punto. Sin introducciones.
2. NO adoptes ninguna personalidad. Actúa como una máquina extractora.
3. Formato JSON estricto con dos claves: 'pregunta' y 'respuesta_objetiva'.
"""

    print(f"\n[2/3] Procesando {muestras} ejemplos con Llama 3.2...")
    
    exitos = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for i, idx in enumerate(indices_aleatorios):
            texto_chunk = textos[idx]
            meta = metadatos[idx]
            
            # Limpiamos la ruta para que solo quede el nombre del archivo
            fuente = meta.get('source', 'Desconocido').split('/')[-1].split('\\')[-1]
            pagina = meta.get('page', 'N/A')
            
            prompt_usuario = f"Fragmento:\n{texto_chunk}"
            
            try:
                respuesta_llm = ollama.chat(
                    model='llama3.2', 
                    format='json',  # Obligamos a Llama a escupir JSON válido
                    messages=[
                        {'role': 'system', 'content': prompt_extractor},
                        {'role': 'user', 'content': prompt_usuario}
                    ],
                    options={
                        'num_ctx': 2048,
                        'temperature': 0.1,  # Temperatura congelada = Cero alucinaciones
                        'num_thread': 6   
                    }
                )
                
                # Parseo seguro
                datos_json = json.loads(respuesta_llm['message']['content'].strip())
                pregunta = datos_json.get('pregunta', '')
                resp_objetiva = datos_json.get('respuesta_objetiva', '')
                
                if not pregunta or not resp_objetiva:
                    continue
                    
                # 3. LA CIRUGÍA: Inyectando la personalidad y la cita con Python
                frase_rust = random.choice(FRASES_RUST)
                cita_exacta = f"[{fuente}, Pág. {pagina}]"
                
                # Dinamismo: 50% probabilidad de que filosofe al inicio o al final
                if random.random() > 0.5:
                    respuesta_final = f"{frase_rust} {resp_objetiva} {cita_exacta}"
                else:
                    respuesta_final = f"{resp_objetiva} {frase_rust} {cita_exacta}"
                
                # Ensamblaje final del JSONL en formato chat para entrenamiento
                linea_jsonl = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT_RUST},
                        {"role": "user", "content": f"Expediente:\n{texto_chunk}\n\nPregunta: {pregunta}"},
                        {"role": "assistant", "content": respuesta_final}
                    ]
                }
                
                f.write(json.dumps(linea_jsonl, ensure_ascii=False) + '\n')
                exitos += 1
                print(f"      [{i+1}/{muestras}] Chunk procesado y ensamblado correctamente.")
                
            except Exception as e:
                print(f"      [{i+1}/{muestras}] ⚠ Error en procesamiento: {e}")

    print(f"\n[3/3] ¡ÉXITO! Dataset impecable guardado en: {OUTPUT_FILE}")
    print(f"      Se generaron {exitos} registros listos para Google Colab.")

if __name__ == "__main__":
    main()