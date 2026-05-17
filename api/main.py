from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import tempfile
import os

from agents.faq_bot import chat_with_bot
from agents.doc_summariser import summarise_document
from agents.vector_store import load_store

app = FastAPI(title="KALNET AI-3 — FAQ Chatbot + Document Summariser")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    try:
        app.state.vector_store = load_store()
        print("FAISS vector store loaded successfully.")
    except Exception as e:
        print(f"Warning: Could not load FAISS store: {e}")
        print("Run build_kb.py first to create the index.")

class FAQRequest(BaseModel):
    question: str
    history: List[dict] = []

class FAQResponse(BaseModel):
    answer: str
    sources: List[str]

@app.get("/")
def root():
    return {"message": "KALNET AI-3 API is running", "endpoints": ["/ai/faq", "/ai/summarise"]}

@app.post("/ai/faq", response_model=FAQResponse)
def faq_endpoint(req: FAQRequest):
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
