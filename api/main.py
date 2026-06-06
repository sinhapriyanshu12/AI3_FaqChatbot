from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import tempfile
import os
import threading
from pathlib import Path

TEMPLATES = Path(__file__).parent.parent / "templates"

app = FastAPI(title="KALNET AI-3 — FAQ Chatbot + Document Summariser")

app.mount("/static", StaticFiles(directory=str(TEMPLATES)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from agents.faq_bot import chat_with_bot
from agents.doc_summariser import summarise_document
from agents.vector_store import load_store

# Global store — loaded in background after startup
_vector_store = None
_store_ready = False

def _load_store_background():
    global _vector_store, _store_ready
    try:
        print("Background: loading FAISS vector store...")
        _vector_store = load_store()
        _store_ready = True
        print("Background: FAISS vector store loaded successfully.")
    except Exception as e:
        print(f"Background: Failed to load FAISS store: {e}")

@app.on_event("startup")
def startup():
    # Start loading in background so port opens immediately
    t = threading.Thread(target=_load_store_background, daemon=True)
    t.start()
    print("Startup complete. Vector store loading in background.")

class FAQRequest(BaseModel):
    question: str
    history: List[dict] = []

class FAQResponse(BaseModel):
    answer: str
    sources: List[str]

@app.get("/", response_class=HTMLResponse)
def landing():
    return (TEMPLATES / "landing.html").read_text(encoding="utf-8")

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return (TEMPLATES / "chat.html").read_text(encoding="utf-8")

@app.get("/summarise", response_class=HTMLResponse)
def summarise_page():
    return (TEMPLATES / "summarise.html").read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {"status": "ok", "vector_store_ready": _store_ready}

@app.post("/ai/faq", response_model=FAQResponse)
def faq_endpoint(req: FAQRequest):
    if not _store_ready:
        return FAQResponse(
            answer="The knowledge base is still loading, please wait 30 seconds and try again.",
            sources=[]
        )
    result = chat_with_bot(req.question, req.history)
    return FAQResponse(answer=result["answer"], sources=result["sources"])

@app.post("/ai/summarise")
async def summarise_endpoint(file: UploadFile = File(...)):
    suffix = ".pdf" if file.filename.endswith(".pdf") else ".docx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        result = summarise_document(tmp_path)
    finally:
        os.unlink(tmp_path)
    return result

