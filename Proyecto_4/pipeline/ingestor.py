"""
=============================================================
 TUTOR ANALÍTICO HÍBRIDO — PASO 1: PIPELINE DE INGESTA RAG
=============================================================
Módulo: ingestor.py

Para cambiar de backend de embeddings edita embedder.py:
    EMBEDDING_BACKEND = "ollama"   # nomic-embed-text (recomendado)
    EMBEDDING_BACKEND = "local"    # TF-IDF + LSA (fallback sin internet)
=============================================================
"""

import re
import json
import hashlib
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

from pypdf import PdfReader
import chromadb
from chromadb.config import Settings

from embedder import get_embedder, BaseEmbedder

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

CORPUS_DIR      = Path(__file__).parent.parent / "corpus"
VECTORSTORE_DIR = Path(__file__).parent.parent / "vectorstore"

CHUNK_SIZE      = 400   # palabras por chunk
CHUNK_OVERLAP   = 80    # solapamiento entre chunks

COLLECTION_NAME = "tutor_seguridad_mx"

# ─── DATACLASS ────────────────────────────────────────────────────────────────

@dataclass
class Chunk:
    chunk_id:   str
    text:       str
    source:     str
    doc_type:   str
    page:       int = 0
    chunk_idx:  int = 0
    word_count: int = 0

# ─── INGESTOR ─────────────────────────────────────────────────────────────────

class CorpusIngestor:

    def __init__(self, backend: str = None):
        print("=" * 60)
        print("  TUTOR ANALÍTICO — Pipeline de Ingesta RAG")
        print("=" * 60)

        print(f"\n[1/4] Cargando embedder...")
        self.embedder: BaseEmbedder = get_embedder(backend)

        print(f"\n[2/4] Inicializando ChromaDB en: {VECTORSTORE_DIR}")
        VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(VECTORSTORE_DIR),
            settings=Settings(anonymized_telemetry=False)
        )

        # Si cambiamos de backend (distinta dimensión), recrear la colección
        existing = [c.name for c in self.client.list_collections()]
        if COLLECTION_NAME in existing:
            existing_col = self.client.get_collection(COLLECTION_NAME)
            stored_dim = self._get_stored_dim()
            if stored_dim and stored_dim != self.embedder.dim:
                print(f"      ⚠  Dimensión almacenada ({stored_dim}) ≠ embedder actual "
                      f"({self.embedder.dim}). Recreando colección...")
                self.client.delete_collection(COLLECTION_NAME)

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"      ✓ Colección '{COLLECTION_NAME}' lista")

    def _get_stored_dim(self) -> int:
        """Lee la dimensión usada en la ingesta anterior (del reporte)."""
        report = VECTORSTORE_DIR / "ingestion_report.json"
        if report.exists():
            with open(report) as f:
                data = json.load(f)
            return data.get("embedding_dim")
        return None

    # ── LIMPIEZA ──────────────────────────────────────────────────────────────

    def _clean(self, raw: str) -> str:
        text = re.sub(r'\r\n|\r', '\n', raw)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'-\n(\w)', r'\1', text)
        text = re.sub(r' {2,}', ' ', text)
        # Eliminar líneas de puntos suspensivos (tablas de contenido)
        text = re.sub(r'\.{4,}', ' ', text)
        # Eliminar líneas de guiones o underscores repetidos
        text = re.sub(r'[-_]{4,}', ' ', text)
        # Eliminar líneas que sean casi puro whitespace o puntuación
        lines = text.split('\n')
        lines = [l for l in lines if len(re.sub(r'[^a-záéíóúüñA-Z]', '', l)) > 3]
        return '\n'.join(lines).strip()

    # ── EXTRACCIÓN ────────────────────────────────────────────────────────────

    MAX_PAGE_CHARS = 3000  # mismo límite que usamos para TXT

    def _extract_pdf(self, path: Path) -> List[Tuple[str, int]]:
        pages = []
        for i, page in enumerate(PdfReader(str(path)).pages):
            cleaned = self._clean(page.extract_text() or "")
            if len(cleaned) <= 50:
                continue

            # Si la página es muy larga (tablas densas, columnas unidas), dividirla
            if len(cleaned) <= self.MAX_PAGE_CHARS:
                pages.append((cleaned, i + 1))
            else:
                words = cleaned.split()
                block, length = [], 0
                for word in words:
                    block.append(word)
                    length += len(word) + 1
                    if length >= self.MAX_PAGE_CHARS:
                        pages.append((" ".join(block), i + 1))
                        block, length = [], 0
                if block:
                    pages.append((" ".join(block), i + 1))
        return pages

    def _extract_txt(self, path: Path) -> List[Tuple[str, int]]:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = self._clean(f.read())
        
        BLOCK_SIZE = 3000  # chars por bloque, seguro para nomic-embed-text
        words = raw.split()
        pages = []
        block, length, page_num = [], 0, 1
        
        for word in words:
            block.append(word)
            length += len(word) + 1
            if length >= BLOCK_SIZE:
                pages.append((" ".join(block), page_num))
                block, length = [], 0
                page_num += 1
        
        if block:
            pages.append((" ".join(block), page_num))
        
        return pages

    # ── CHUNKING ──────────────────────────────────────────────────────────────

    def _chunk(self, text: str, source: str, doc_type: str,
               page: int, base_idx: int = 0) -> List[Chunk]:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text)
                     if len(s.strip()) > 15]
        chunks, words, length, idx = [], [], 0, base_idx

        for sent in sentences:
            w = sent.split()
            if length + len(w) > CHUNK_SIZE and words:
                cid = hashlib.md5(f"{source}_{page}_{idx}".encode()).hexdigest()[:16]
                chunks.append(Chunk(cid, " ".join(words), source, doc_type, page, idx, length))
                idx += 1
                words  = words[-CHUNK_OVERLAP:] + w
                length = len(words)
            else:
                words.extend(w)
                length += len(w)

        if words:
            cid = hashlib.md5(f"{source}_{page}_{idx}".encode()).hexdigest()[:16]
            chunks.append(Chunk(cid, " ".join(words), source, doc_type, page, idx, length))
        return chunks

    # ── INDEXACIÓN ────────────────────────────────────────────────────────────

    def _index(self, chunks: List[Chunk], embeddings: np.ndarray) -> None:
        BATCH = 64
        for i in range(0, len(chunks), BATCH):
            b = chunks[i:i+BATCH]
            self.collection.upsert(
                ids=[c.chunk_id for c in b],
                documents=[c.text for c in b],
                embeddings=embeddings[i:i+len(b)].tolist(),
                metadatas=[{
                    "source": c.source, "doc_type": c.doc_type,
                    "page": c.page, "chunk_idx": c.chunk_idx,
                    "word_count": c.word_count
                } for c in b]
            )

    # ── PIPELINE PRINCIPAL ────────────────────────────────────────────────────

    def run(self) -> Dict:
        all_chunks: List[Chunk] = []
        stats = {"documentos": [], "embedding_backend": self.embedder.name,
                 "embedding_dim": self.embedder.dim,
                 "total_chunks": 0, "total_palabras": 0}

        print(f"\n[3/4] Procesando corpus en: {CORPUS_DIR}")
        print("-" * 60)

        files = sorted(list(CORPUS_DIR.glob("*.pdf")) + list(CORPUS_DIR.glob("*.txt")))
        if not files:
            print("  ⚠ No se encontraron archivos.")
            return stats

        for fp in files:
            dtype  = fp.suffix.lstrip(".")
            source = fp.name
            print(f"\n  📄 {source}")

            pages = self._extract_pdf(fp) if dtype == "pdf" else self._extract_txt(fp)
            doc_chunks, idx = [], 0
            for text, pnum in pages:
                pc = self._chunk(text, source, dtype, pnum, idx)
                doc_chunks.extend(pc)
                idx += len(pc)

            words = sum(c.word_count for c in doc_chunks)
            print(f"     ↳ Páginas: {len(pages)} | Chunks: {len(doc_chunks)} | Palabras: {words:,}")
            stats["documentos"].append({"archivo": source, "tipo": dtype,
                "paginas": len(pages), "chunks": len(doc_chunks), "palabras": words})
            all_chunks.extend(doc_chunks)

        # Entrenar embedder si es necesario (solo para backend local)
        all_texts = [c.text for c in all_chunks]
        self.embedder.fit(all_texts)

        print(f"\n[4/4] Vectorizando {len(all_chunks)} chunks con {self.embedder.name}...")
        embeddings = self.embedder.encode(all_texts)

        print(f"      Indexando en ChromaDB...")
        self._index(all_chunks, embeddings)

        stats["total_chunks"]   = len(all_chunks)
        stats["total_palabras"] = sum(c.word_count for c in all_chunks)

        print("\n" + "=" * 60)
        print("  ✅ INGESTA COMPLETADA")
        print("=" * 60)
        print(f"  Backend          : {self.embedder.name}")
        print(f"  Dimensiones      : {self.embedder.dim}")
        print(f"  Chunks indexados : {self.collection.count()}")
        print(f"  Palabras totales : {stats['total_palabras']:,}")

        report = VECTORSTORE_DIR / "ingestion_report.json"
        with open(report, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"  Reporte          : {report}")
        return stats


if __name__ == "__main__":
    ingestor = CorpusIngestor()
    ingestor.run()