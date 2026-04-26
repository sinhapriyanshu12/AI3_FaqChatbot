import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from data.pipeline.ingest import ingest_folder
from agents.vector_store import build_store

if __name__ == "__main__":
    print("Ingesting documents...")
    chunks = ingest_folder("data/raw")
    print(f"Total chunks: {len(chunks)}")
    print("Building FAISS index (first run downloads ~80MB model, please wait)...")
    build_store(chunks)
    print("Done. Index saved to data/processed/faiss_index/")