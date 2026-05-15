import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from data.pipeline.ingest import ingest_folder
from agents.vector_store import build_store

if __name__ == "__main__":
    print("Ingesting documents...")
    chunks = ingest_folder("data/raw")
    print(f"Total chunks: {len(chunks)}")
    if len(chunks) == 0:
        print("ERROR: No documents found in data/raw/")
        print("Please add PDF or DOCX files to the data/raw/ folder first.")
        sys.exit(1)
    print("Building FAISS index (first run downloads ~80MB model, please wait)...")
    build_store(chunks)
    print("Done. Index saved to data/processed/faiss_index/")
