# api/main.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import tempfile, os
from agents.faq_bot import chat_with_bot
from agents.doc_summariser import summarise_document
from agents.vector_store import load_store

app = FastAPI(title="KALNET AI-3")

# Load FAISS once at startup (not inside route handlers)
@app.on_event("startup")
def startup():
    app.state.vector_store = load_store()
    print("FAISS vector store loaded.")

class FAQRequest(BaseModel):
    question: str
    history: List[dict] = []

class FAQResponse(BaseModel):
    answer: str
    sources: List[str]

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
    result = summarise_document(tmp_path)
    os.unlink(tmp_path)
    return result