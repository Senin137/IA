"""
=============================================================
 TUTOR ANALÍTICO — RETRIEVER SEMÁNTICO (Paso 1)
=============================================================
Módulo: retriever.py

Lee el backend de embeddings del reporte de ingesta para
garantizar que query y documentos usen el mismo espacio vectorial.
=============================================================
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings

from embedder import get_embedder, BaseEmbedder

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

VECTORSTORE_DIR = Path(__file__).parent.parent / "vectorstore"
COLLECTION_NAME = "tutor_seguridad_mx"
TOP_K           = 5
MIN_SIMILARITY  = 0.10

# ─── DATACLASS ────────────────────────────────────────────────────────────────

@dataclass
class RetrievedChunk:
    text:       str
    source:     str
    page:       int
    chunk_idx:  int
    similarity: float
    citation:   str   # e.g. "[dossier2.pdf, Pág. 3]"

# ─── RETRIEVER ────────────────────────────────────────────────────────────────

class SemanticRetriever:
    """
    Recupera los K chunks más relevantes para una consulta.
    Usa el mismo backend de embeddings que usó el ingestor
    (detectado automáticamente desde el reporte de ingesta).
    """

    def __init__(self):
        if not VECTORSTORE_DIR.exists():
            raise FileNotFoundError(
                "Vectorstore no encontrado. "
                "Ejecuta primero: python run_pipeline.py --only-ingest"
            )

        # Detectar backend usado en la ingesta
        backend = self._detect_backend()
        print(f"[Retriever] Backend detectado: {backend}")

        self.embedder: BaseEmbedder = get_embedder(backend)

        # Para el backend local, cargar el modelo entrenado
        if backend == "local":
            from embedder import LocalEmbedder
            local = LocalEmbedder()
            if not local.load():
                raise RuntimeError(
                    "Modelo local no encontrado. Re-ejecuta la ingesta."
                )
            self.embedder = local

        self.client = chromadb.PersistentClient(
            path=str(VECTORSTORE_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_collection(COLLECTION_NAME)
        print(f"[Retriever] Chunks disponibles: {self.collection.count()}")

    def _detect_backend(self) -> str:
        """Lee el backend usado en la última ingesta."""
        report = VECTORSTORE_DIR / "ingestion_report.json"
        if report.exists():
            with open(report) as f:
                data = json.load(f)
            raw = data.get("embedding_backend", "local")
            # "ollama/nomic-embed-text" → "ollama"
            return raw.split("/")[0]
        return "local"

    def retrieve(self, query: str, top_k: int = TOP_K,
                 filter_source: Optional[str] = None) -> List[RetrievedChunk]:
        """
        Busca los chunks más similares a la query.

        Args:
            query:         Pregunta del usuario.
            top_k:         Máximo de chunks a retornar.
            filter_source: Filtrar por nombre de archivo fuente.

        Returns:
            Lista de RetrievedChunk ordenada por similitud desc.
        """
        qvec = self.embedder.encode_one(query)
        where = {"source": filter_source} if filter_source else None

        results = self.collection.query(
            query_embeddings=[qvec],
            n_results=min(top_k, self.collection.count()),
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        chunks = []
        for doc, meta, dist in zip(results["documents"][0],
                                    results["metadatas"][0],
                                    results["distances"][0]):
            sim = round(max(0.0, 1.0 - dist), 4)
            if sim < MIN_SIMILARITY:
                continue
            page = meta["page"]
            citation = (f"[{meta['source']}, Pág. {page}]"
                        if page > 0 else f"[{meta['source']}]")
            chunks.append(RetrievedChunk(
                text=doc, source=meta["source"], page=page,
                chunk_idx=meta["chunk_idx"], similarity=sim, citation=citation
            ))
        return chunks

    def build_context(self, chunks: List[RetrievedChunk]) -> str:
        """Ensambla el contexto para inyectar al LLM."""
        if not chunks:
            return "No se encontró información relevante en el corpus."
        parts = [f"--- FUENTE {i}: {c.citation} ---\n{c.text}\n"
                 for i, c in enumerate(chunks, 1)]
        return "\n".join(parts)

    def query_and_show(self, query: str, top_k: int = TOP_K) -> List[RetrievedChunk]:
        """Modo diagnóstico: imprime resultados en consola."""
        print(f"\n{'='*60}")
        print(f"  CONSULTA: {query}")
        print(f"{'='*60}")
        chunks = self.retrieve(query, top_k=top_k)
        if not chunks:
            print("  ⚠ Sin resultados relevantes (probablemente fuera del corpus)")
        for i, c in enumerate(chunks, 1):
            print(f"  [{i}] {c.citation} | Sim: {c.similarity:.4f}")
            print(f"       {c.text[:220]}...\n")
        return chunks


if __name__ == "__main__":
    r = SemanticRetriever()
    for q in [
        "entidades federativas con mayor índice de homicidios dolosos",
        "evolución tasa de extorsión sectores más afectados",
        "impacto violencia deserción escolar educación",
        "relación ingresos mujeres violencia de género México",
        "cárteles Michoacán CJNG crimen organizado",
    ]:
        r.query_and_show(q)