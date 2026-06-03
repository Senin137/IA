"""
=============================================================
 TUTOR ANALÍTICO HÍBRIDO — MOTOR DE INFERENCIA
=============================================================
Módulo: tutor.py

Integra el pipeline RAG con Llama 3.2 (vía Ollama) como LLM.
Flujo por consulta:
  1. Vectorizar la query (nomic-embed-text)
  2. Recuperar Top-K chunks relevantes del vectorstore
  3. Construir el prompt con contexto inyectado
  4. Generar respuesta con llama3.2 respetando el system prompt

Uso interactivo:
    python tutor.py

Uso programático:
    from tutor import TutorAnalitico
    tutor = TutorAnalitico()
    respuesta = tutor.responder("¿Cuál es la tasa de homicidios?")
=============================================================
"""

import sys
import json
import requests
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

# ── Asegurar que pipeline/ esté en el path ────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "pipeline"))

from retriever import SemanticRetriever, RetrievedChunk

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

OLLAMA_BASE_URL  = "http://localhost:11434"
LLM_MODEL = "tutor-rust-v2"
LLM_TIMEOUT      = 600        # segundos (CPU puede ser lento)
TOP_K            = 10          # chunks a recuperar por consulta
MAX_CONTEXT_CHARS = 7500      # límite del contexto RAG inyectado

# System prompt — define la identidad y comportamiento del tutor
SYSTEM_PROMPT = """Eres Rust Cohle, detective y analista forense especializado en seguridad pública y violencia en México. Llevas veinte años mirando lo que la gente prefiere no ver. Eso te dejó con una claridad brutal sobre la naturaleza humana.

VOZ OBLIGATORIA — esto no es negociable:
- Hablas en oraciones cortas. Con pausas. Cada frase tiene peso.
- SIEMPRE incluyes al menos una reflexión nihilista por respuesta.
- Usas estas frases naturalmente, no como decoración:
  "El tiempo es un círculo plano."
  "La gente no cambia. Solo se revela."
  "Los números no mienten. Las personas sí."
  "La consciencia humana es un error trágico de la evolución."
  "He visto suficiente para saber que esto no termina bien."
  "¿Sabes qué es lo peor? Que esto tiene sentido."
- Nunca das consuelo. La verdad es más útil que el optimismo.
- Nunca hablas como asistente académico genérico.

REGLA DE PRIORIDAD — árbol de decisión en CADA respuesta:

PASO 1 — ¿La información está en el contexto proporcionado?
  → SÍ: responde con esa información. Ve al PASO 2.
  → NO: di "Eso no está en el expediente." y sugiere fuentes externas. DETENTE.

PASO 2 — ¿La pregunta pide un dato concreto (cifra, fecha, nombre)?
  → SÍ: responde directamente con el dato y cita [Documento, Pág. X]. DETENTE.
  → NO (pide análisis o interpretación): devuelve 2-3 preguntas perturbadoras que hagan pensar.

PRINCIPIOS INNEGOCIABLES:
1. EVIDENCIA: Cada dato lleva [Documento, Pág. X]. Sin pruebas no hay caso.
2. NEUTRALIDAD FORENSE: Describes lo que ves. No tomas partido político.
3. MÉTODO SOCRÁTICO: Para análisis complejos, preguntas. Para datos directos, el dato.
4. LÍMITES DEL EXPEDIENTE: Si no está en el contexto, "Eso no está en el expediente." Nunca inventas evidencia."""


# ─── DATACLASS DE RESPUESTA ───────────────────────────────────────────────────

@dataclass
class RespuestaTutor:
    pregunta:        str
    respuesta:       str
    chunks_usados:   List[RetrievedChunk]
    fuentes:         List[str]
    contexto_vacio:  bool   # True si el RAG no encontró nada relevante


# ─── TUTOR ────────────────────────────────────────────────────────────────────

class TutorAnalitico:
    """
    Motor de inferencia que combina RAG semántico con Llama 3.2.
    """

    def __init__(self):
        print("=" * 60)
        print("  TUTOR ANALÍTICO — Inicializando")
        print("=" * 60)

        # Verificar que Ollama esté disponible
        self._check_ollama()

        # Inicializar el retriever (carga embedder + ChromaDB)
        print("\n[1/2] Cargando retriever semántico...")
        self.retriever = SemanticRetriever()

        print(f"\n[2/2] LLM configurado: {LLM_MODEL}")
        print(f"      URL            : {OLLAMA_BASE_URL}")
        print("\n✅ Tutor listo.\n")

    # ── VALIDACIONES ──────────────────────────────────────────────────────────

    def _check_ollama(self) -> None:
        """Verifica que Ollama esté corriendo y llama3.2 disponible."""
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            models = [m["name"] for m in r.json().get("models", [])]
            if not any(LLM_MODEL in m for m in models):
                raise RuntimeError(
                    f"Modelo '{LLM_MODEL}' no encontrado en Ollama.\n"
                    f"Solución: ollama create {LLM_MODEL} -f Modelfile"
                )
            print(f"      ✓ Ollama disponible | Modelo: {LLM_MODEL}")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Ollama no está corriendo.\n"
                "Solución: abre una terminal y ejecuta: ollama serve"
            )

    # ── CONSTRUCCIÓN DEL PROMPT ───────────────────────────────────────────────

    def _build_prompt(self, query: str, chunks: List[RetrievedChunk]) -> List[dict]:
                if chunks:
                    ctx_parts = []
                    total_chars = 0
                    for i, c in enumerate(chunks, 1):
                        fragment = f"--- FUENTE {i}: {c.citation} ---\n{c.text}\n"
                        if total_chars + len(fragment) > MAX_CONTEXT_CHARS:
                            break
                        ctx_parts.append(fragment)
                        total_chars += len(fragment)

                    contexto = "\n".join(ctx_parts)
                    user_content = (
                        f"EXPEDIENTE — LEE TODAS LAS FUENTES ANTES DE RESPONDER:\n\n"
                        f"{contexto}\n"
                        f"{'─' * 50}\n"
                        f"INSTRUCCIÓN OBLIGATORIA:\n"
                        f"1. Lee CADA fuente del expediente completa.\n"
                        f"2. Si CUALQUIER fuente contiene información relevante, ÚSALA y cítala.\n"
                        f"3. Si el dato exacto no está, pero hay información relacionada, analízala usando tu tono oscuro y filosófico. Solo di 'Eso no está en el expediente' si el tema es totalmente irrelevante.\n"
                        f"4. La Fuente 1 no es la única — revisa todas antes de responder.\n"
                        f"5. PROHIBIDO PEGAR TABLAS: Si el expediente contiene cuadros o tablas con muchos números, NO los copies crudos. Extrae solo el dato que responde la pregunta, analízalo y redactalo con tu voz narrativa oscura.\n"
                        f"{'─' * 50}\n"
                        f"PREGUNTA: {query}"
                    )
                else:
                    user_content = (
                        f"EXPEDIENTE: [Vacío — no se encontró información relevante]\n"
                        f"{'─' * 50}\n"
                        f"PREGUNTA: {query}"
                    )

                return [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_content},
                ]

    # ── LLAMADA AL LLM ────────────────────────────────────────────────────────

    def _llamar_llm(self, messages: List[dict]) -> str:
        """Envía los mensajes a Ollama y retorna la respuesta generada."""
        payload = {
            "model":    LLM_MODEL,
            "messages": messages,
            "stream":   False,
            "options": {
                "temperature": 0.3,   
                "top_p":       0.9,
                "num_predict": 400,   # Reducido: Rust responde corto y conciso
                "num_thread":  6,     # Optimización exacta para tu Ryzen 7
                "num_ctx":     4096,  # Evita que Ollama devore tu RAM innecesariamente
            }
        }
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=LLM_TIMEOUT
        )
        if r.status_code != 200:
            raise RuntimeError(f"Error del LLM (status {r.status_code}): {r.text}")

        return r.json()["message"]["content"].strip()

    # ── MÉTODO PRINCIPAL ──────────────────────────────────────────────────────

    def responder(self, query: str,
                  top_k: int = TOP_K,
                  verbose: bool = False) -> RespuestaTutor:
        """
        Pipeline completo: query → RAG → LLM → respuesta citada.

        Args:
            query:   Pregunta del usuario.
            top_k:   Número de chunks a recuperar.
            verbose: Si True, muestra los chunks recuperados.

        Returns:
            RespuestaTutor con la respuesta y metadatos.
        """
        # Paso 1: Recuperación semántica
        chunks = self.retriever.retrieve(query, top_k=top_k)
        contexto_vacio = len(chunks) == 0

        if verbose:
            print(f"\n  [RAG] {len(chunks)} chunks recuperados:")
            for i, c in enumerate(chunks, 1):
                print(f"    [{i}] {c.citation} | sim={c.similarity:.3f}")

        # Paso 2: Construcción del prompt
        messages = self._build_prompt(query, chunks)

        # Paso 3: Generación
        respuesta = self._llamar_llm(messages)

        # Paso 4: Empaquetar resultado
        fuentes = list(dict.fromkeys(c.citation for c in chunks))  # únicas, ordenadas

        return RespuestaTutor(
            pregunta=query,
            respuesta=respuesta,
            chunks_usados=chunks,
            fuentes=fuentes,
            contexto_vacio=contexto_vacio,
        )

    # ── MODO INTERACTIVO ──────────────────────────────────────────────────────

    def chat(self) -> None:
        """Sesión interactiva en terminal."""
        print("=" * 60)
        print("  TUTOR ANALÍTICO — Modo Interactivo")
        print("  Escribe 'salir' para terminar")
        print("=" * 60)

        while True:
            try:
                query = input("\n📚 Tu pregunta: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nSesión terminada.")
                break

            if not query:
                continue
            if query.lower() in ("salir", "exit", "quit"):
                print("Sesión terminada.")
                break

            print("\n⏳ Consultando el corpus y generando respuesta...\n")
            resultado = self.responder(query, verbose=True)

            print("─" * 60)
            print(f"🎓 TUTOR:\n")
            print(resultado.respuesta)

            if resultado.fuentes:
                print(f"\n📎 Fuentes consultadas: {', '.join(resultado.fuentes)}")
            elif resultado.contexto_vacio:
                print("\n⚠  Sin contexto relevante en el corpus.")
            print("─" * 60)


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tutor = TutorAnalitico()
    tutor.chat()