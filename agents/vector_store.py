import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Absolute path — works both locally and on Render
BASE_DIR = Path(__file__).parent.parent
DEFAULT_INDEX_PATH = str(BASE_DIR / "data" / "processed" / "faiss_index")


def get_embeddings():
    print("Loading embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    print("Embeddings loaded.")
    return embeddings


def build_store(docs, save_path=None):
    if save_path is None:
        save_path = DEFAULT_INDEX_PATH
    os.makedirs(save_path, exist_ok=True)
    embeddings = get_embeddings()
    store = FAISS.from_documents(docs, embeddings)
    store.save_local(save_path)
    print(f"FAISS index saved to {save_path}")
    return store


def load_store(index_path=None):
    if index_path is None:
        index_path = DEFAULT_INDEX_PATH
    print(f"Loading FAISS index from: {index_path}")
    embeddings = get_embeddings()
    store = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    print("FAISS loaded.")
    return store



