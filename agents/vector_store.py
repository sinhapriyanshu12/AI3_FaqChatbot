"""Shared vector store helpers.

Owned by Priyanshu.
"""

from pathlib import Path


def build_store(docs_folder: str) -> None:
    """Build the FAISS vector store from documents."""
    docs_path = Path(docs_folder)
    raise NotImplementedError(f"Implement FAISS build using documents from {docs_path}")


def load_store(index_path: str):
    """Load an existing FAISS vector store."""
    path = Path(index_path)
    raise NotImplementedError(f"Implement FAISS load from {path}")
