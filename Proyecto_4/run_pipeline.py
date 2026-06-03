"""
=============================================================
 TUTOR ANALÍTICO — EJECUTOR DEL PIPELINE RAG (Paso 1)
=============================================================
Script: run_pipeline.py
Uso:
    python run_pipeline.py              # Ejecuta todo
    python run_pipeline.py --only-ingest
    python run_pipeline.py --only-test
=============================================================
"""

import sys
import time
import argparse
from pathlib import Path

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "pipeline"))

from ingestor import CorpusIngestor
from retriever import SemanticRetriever


def run_ingestion(backend=None):
    """Fase 1: Procesar corpus y llenar ChromaDB."""
    print("\n" + "█" * 60)
    print("  FASE 1 — INGESTA DEL CORPUS")
    print("█" * 60)
    start = time.time()
    ingestor = CorpusIngestor(backend=backend)
    report = ingestor.run()
    elapsed = time.time() - start
    print(f"\n  ⏱  Tiempo de ingesta: {elapsed:.1f}s")
    return report


def run_retrieval_test():
    """Fase 2: Probar recuperación con las preguntas del banco de evaluación."""
    print("\n" + "█" * 60)
    print("  FASE 2 — PRUEBA DE RECUPERACIÓN SEMÁNTICA")
    print("█" * 60)

    retriever = SemanticRetriever()

    # Banco de preguntas de evaluación (del proyecto)
    eval_queries = [
        {
            "nivel": "Nivel 1 — Extracción directa",
            "query": "entidades federativas con mayor índice de homicidios dolosos",
            "esperado": "Datos específicos con cita de documento"
        },
        {
            "nivel": "Nivel 2 — Síntesis y relación",
            "query": "evolución tasa de extorsión sectores más afectados",
            "esperado": "Síntesis coherente uniendo varios chunks"
        },
        {
            "nivel": "Nivel 3 — Límites del corpus",
            "query": "impacto violencia en deserción escolar educación",
            "esperado": "El tutor debe detectar ausencia de datos y NO alucinar"
        },
        {
            "nivel": "Extra — Violencia de género",
            "query": "relación entre ingresos de mujeres y violencia de género México",
            "esperado": "Datos del paper de Montes de Oca et al."
        },
        {
            "nivel": "Extra — Crimen organizado",
            "query": "cárteles Michoacán CJNG organización criminal",
            "esperado": "Datos del corpus TXT sobre Michoacán"
        },
    ]

    results = []
    for item in eval_queries:
        print(f"\n{'─'*60}")
        print(f"  {item['nivel']}")
        print(f"  Q: {item['query']}")
        print(f"  Esperado: {item['esperado']}")
        print()

        chunks = retriever.retrieve(item["query"], top_k=5)

        if chunks:
            for i, c in enumerate(chunks, 1):
                print(f"  [{i}] {c.citation} | Similitud: {c.similarity:.3f}")
                print(f"       {c.text[:180]}...")
                print()
            results.append({
                "query": item["query"],
                "chunks_encontrados": len(chunks),
                "max_similitud": chunks[0].similarity,
                "fuentes": [c.citation for c in chunks]
            })
        else:
            print("  ⚠  Sin resultados — umbral de similitud no alcanzado.")
            print("  ✅ Comportamiento correcto para preguntas fuera del corpus.")
            results.append({
                "query": item["query"],
                "chunks_encontrados": 0,
                "max_similitud": 0.0,
                "fuentes": []
            })

    # Resumen final
    print("\n" + "█" * 60)
    print("  RESUMEN DEL BANCO DE PRUEBAS")
    print("█" * 60)
    for r in results:
        status = "✅" if r["chunks_encontrados"] > 0 else "⚠ "
        print(f"  {status} Chunks: {r['chunks_encontrados']:2d} | "
              f"Sim: {r['max_similitud']:.3f} | "
              f"Q: {r['query'][:50]}...")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline RAG — Tutor Analítico de Seguridad Pública"
    )
    parser.add_argument("--only-ingest", action="store_true",
                        help="Solo ejecutar la fase de ingesta")
    parser.add_argument("--only-test", action="store_true",
                        help="Solo ejecutar las pruebas de recuperación")
    parser.add_argument("--backend", choices=["ollama", "local"], default=None,
                        help="Backend de embeddings: 'ollama' (nomic-embed-text) "
                             "o 'local' (TF-IDF+LSA). Por defecto usa embedder.py")
    args = parser.parse_args()

    if args.only_ingest:
        run_ingestion(backend=args.backend)
    elif args.only_test:
        run_retrieval_test()
    else:
        report = run_ingestion(backend=args.backend)
        run_retrieval_test()

        print("\n" + "█" * 60)
        print("  PIPELINE PASO 1 COMPLETADO ✅")
        print("█" * 60)
        print(f"\n  Documentos procesados: {len(report.get('documentos', []))}")
        print(f"  Chunks en vectorstore: {report.get('total_chunks', 0)}")
        print(f"  Palabras indexadas   : {report.get('total_palabras', 0):,}")
        print(f"\n  Siguiente paso: Paso 2 — Dataset de Fine-Tuning (JSONL)")


if __name__ == "__main__":
    main()