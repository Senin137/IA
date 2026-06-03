"""
=============================================================
 TUTOR ANALÍTICO — MÓDULO DE EMBEDDINGS
=============================================================
Módulo: embedder.py

Soporta dos backends intercambiables:

  BACKEND = "ollama"  → nomic-embed-text vía Ollama REST API
                         Requiere: ollama serve (corriendo)
                         Dimensiones: 768
                         Calidad: ⭐⭐⭐⭐⭐ (semántica real en español)

  BACKEND = "local"   → TF-IDF + LSA (sklearn, sin internet)
                         Requiere: nada externo
                         Dimensiones: 128
                         Calidad: ⭐⭐⭐ (léxico, bueno para corpus pequeño)

Cambiar el backend: editar EMBEDDING_BACKEND abajo, o pasar
el argumento al construir el embedder:
    emb = get_embedder("ollama")
    emb = get_embedder("local")
=============================================================
"""

import os
import json
import pickle
import requests
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

# Cambia aquí para alternar entre backends
EMBEDDING_BACKEND = "ollama"   # "ollama" | "local"

# Ollama
OLLAMA_BASE_URL   = "http://localhost:11434"
OLLAMA_MODEL      = "nomic-embed-text"
OLLAMA_DIM        = 768          # dimensiones de nomic-embed-text
OLLAMA_TIMEOUT    = 30           # segundos por request
OLLAMA_BATCH_SIZE = 16           # chunks por lote (ajustar si hay OOM)

# Local (TF-IDF + LSA)
LOCAL_DIM         = 128
MODELS_DIR        = Path(__file__).parent.parent / "vectorstore" / "models"


# ─── INTERFAZ BASE ────────────────────────────────────────────────────────────

class BaseEmbedder(ABC):
    """Interfaz común para todos los backends de embedding."""

    @property
    @abstractmethod
    def dim(self) -> int:
        """Dimensiones del vector de embedding."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre descriptivo del backend."""

    @abstractmethod
    def fit(self, texts: List[str]) -> None:
        """Entrena el embedder (no-op para Ollama)."""

    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Convierte una lista de textos en vectores normalizados.
        Retorna ndarray de shape (len(texts), dim).
        """

    def encode_one(self, text: str) -> List[float]:
        """Vectoriza un único texto. Útil para queries."""
        return self.encode([text])[0].tolist()


# ─── BACKEND: OLLAMA ─────────────────────────────────────────────────────────

class OllamaEmbedder(BaseEmbedder):
    """
    Genera embeddings usando nomic-embed-text a través de la API
    REST local de Ollama.

    Prerrequisitos en tu máquina:
        1. ollama serve          (o que esté corriendo como servicio)
        2. ollama pull nomic-embed-text

    nomic-embed-text ventajas para este proyecto:
        - Entrenado en 300M+ documentos en múltiples idiomas
        - Excelente comprensión del español
        - 768 dimensiones → mucho más expresivo que LSA
        - Corre completamente en CPU (tu Ryzen 7 3700U)
        - ~274 MB de RAM cuando está cargado
    """

    @property
    def dim(self) -> int:
        return OLLAMA_DIM

    @property
    def name(self) -> str:
        return f"ollama/{OLLAMA_MODEL}"

    def _check_ollama(self) -> bool:
        """Verifica que Ollama esté corriendo y el modelo disponible."""
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if r.status_code != 200:
                return False
            models = [m["name"] for m in r.json().get("models", [])]
            # nomic-embed-text puede aparecer con o sin :latest
            return any(OLLAMA_MODEL in m for m in models)
        except requests.exceptions.ConnectionError:
            return False

    def fit(self, texts: List[str]) -> None:
        """Ollama no requiere entrenamiento — modelo ya está listo."""
        pass

    MAX_CHARS = 6000  # ~8192 tokens de nomic-embed-text, con margen de seguridad

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            # Truncar si excede el límite de contexto de Ollama
            safe_text = text.strip()
            if not safe_text:
                safe_text = "[vacío]"
            elif len(safe_text) > self.MAX_CHARS:
                safe_text = safe_text[:self.MAX_CHARS]

            payload = {
                "model": OLLAMA_MODEL,
                "input": [safe_text]
            }
            r = requests.post(
                f"{OLLAMA_BASE_URL}/api/embed",
                json=payload,
                timeout=OLLAMA_TIMEOUT
            )
            if r.status_code != 200:
                print(f"\n  ERROR 400 en chunk:")
                print(f"  Longitud: {len(safe_text)} chars")
                print(f"  Respuesta: {r.text}")
                print(f"  Texto: {repr(safe_text[:200])}")
                raise ValueError(f"Ollama rechazó el chunk (status {r.status_code})")
            data = r.json()

            embeddings = data.get("embeddings", [])
            if not embeddings or len(embeddings[0]) == 0:
                raise ValueError(f"Ollama devolvió embedding vacío para: {text[:50]}")
            vectors.append(embeddings[0])

        return np.array(vectors, dtype=np.float32)

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Vectoriza todos los textos en lotes.
        Muestra progreso para corpus grandes.
        """
        if not self._check_ollama():
            raise RuntimeError(
                f"Ollama no está disponible o el modelo '{OLLAMA_MODEL}' "
                f"no está descargado.\n"
                f"Solución:\n"
                f"  1. Abre una terminal y ejecuta: ollama serve\n"
                f"  2. Descarga el modelo: ollama pull {OLLAMA_MODEL}\n"
                f"  3. Vuelve a ejecutar el pipeline."
            )

        all_vectors = []
        total = len(texts)

        for i in range(0, total, OLLAMA_BATCH_SIZE):
            batch = texts[i:i + OLLAMA_BATCH_SIZE]
            vecs = self._embed_batch(batch)
            all_vectors.append(vecs)

            end = min(i + OLLAMA_BATCH_SIZE, total)
            print(f"      Embeddings: {end}/{total} chunks procesados...", end="\r")

        print()  # salto de línea tras el progreso
        result = np.vstack(all_vectors)
        return normalize(result)   # normalización L2 para similitud coseno


# ─── BACKEND: LOCAL (TF-IDF + LSA) ───────────────────────────────────────────

class LocalEmbedder(BaseEmbedder):
    """
    Embedding 100% local. Útil como fallback si Ollama no está disponible
    o para pruebas rápidas sin levantar el servidor.
    """

    @property
    def dim(self) -> int:
        return LOCAL_DIM

    @property
    def name(self) -> str:
        return "local/tfidf-lsa"

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            max_features=20000,
            min_df=1,
            sublinear_tf=True,
            strip_accents=None,
        )
        self.svd = TruncatedSVD(n_components=LOCAL_DIM, random_state=42)
        self.is_fitted = False
        self._model_path = MODELS_DIR / "tfidf_lsa.pkl"

    def fit(self, texts: List[str]) -> None:
        print(f"      Entrenando TF-IDF sobre {len(texts)} textos...")
        tfidf = self.vectorizer.fit_transform(texts)
        print(f"      Vocabulario: {len(self.vectorizer.vocabulary_):,} términos")
        print(f"      Aplicando SVD a {LOCAL_DIM} dimensiones...")
        self.svd.fit(tfidf)
        self.is_fitted = True
        self._save()
        print(f"      Varianza explicada: {self.svd.explained_variance_ratio_.sum():.1%}")

    def encode(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Llama fit() antes de encode().")
        tfidf = self.vectorizer.transform(texts)
        vecs  = self.svd.transform(tfidf)
        return normalize(vecs)

    def _save(self) -> None:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        with open(self._model_path, 'wb') as f:
            pickle.dump({'vectorizer': self.vectorizer, 'svd': self.svd}, f)

    def load(self) -> bool:
        if self._model_path.exists():
            with open(self._model_path, 'rb') as f:
                data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.svd        = data['svd']
            self.is_fitted  = True
            return True
        return False


# ─── FACTORY ──────────────────────────────────────────────────────────────────

def get_embedder(backend: Optional[str] = None) -> BaseEmbedder:
    """
    Devuelve el embedder configurado.

    Args:
        backend: "ollama" | "local" | None (usa EMBEDDING_BACKEND)

    Si se pide "ollama" pero no está disponible, avisa claramente
    en lugar de caer silenciosamente a local.
    """
    chosen = (backend or EMBEDDING_BACKEND).lower()

    if chosen == "ollama":
        embedder = OllamaEmbedder()
        print(f"      Backend: {embedder.name} ({embedder.dim} dims)")
        print(f"      URL    : {OLLAMA_BASE_URL}")
        return embedder

    elif chosen == "local":
        embedder = LocalEmbedder()
        print(f"      Backend: {embedder.name} ({embedder.dim} dims)")
        return embedder

    else:
        raise ValueError(f"Backend desconocido: '{chosen}'. Usa 'ollama' o 'local'.")