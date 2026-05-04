#!/usr/bin/env python3
"""CLI: ingest PDFs or URLs into CogniRAG."""
import argparse, sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag_pipeline import RAGPipeline


def main():
    p = argparse.ArgumentParser(description="CogniRAG document ingestion CLI")
    p.add_argument("--source", action="append", help="PDF path or URL (repeatable)")
    p.add_argument("--reset", action="store_true", help="Clear vector store first")
    p.add_argument("--mmr", action="store_true", help="Use MMR retrieval")
    args = p.parse_args()

    if not args.source and not args.reset:
        p.print_help(); sys.exit(1)

    pipeline = RAGPipeline()
    if args.mmr:
        pipeline.set_mmr(True)

    if args.reset:
        pipeline.reset()
        print("✅ Vector store cleared")

    for src in (args.source or []):
        kind = "url" if src.startswith("http") else "pdf"
        print(f"⏳ Processing {kind.upper()}: {src}")
        try:
            n = pipeline.add_document(src, kind)
            print(f"   ✅ {n} chunks stored")
        except Exception as e:
            print(f"   ❌ {e}"); sys.exit(1)

    print(f"\n🎉 Done! Total chunks: {pipeline.doc_count}")


if __name__ == "__main__":
    main()