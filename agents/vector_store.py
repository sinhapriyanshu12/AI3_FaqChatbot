import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)

def build_store(docs, save_path="data/processed/faiss_index"):
    os.makedirs(save_path, exist_ok=True)
    embeddings = get_embeddings()
    store = FAISS.from_documents(docs, embeddings)
    store.save_local(save_path)
    print(f"FAISS index saved to {save_path}")
    return store

def load_store(index_path="data/processed/faiss_index"):
    embeddings = get_embeddings()
    store = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return store