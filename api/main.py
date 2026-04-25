"""FastAPI entry point."""

from __future__ import annotations

from pathlib import Path
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile

from agents.doc_summariser import summarise_document
from agents.faq_bot import chat_with_bot
from agents.vector_store import build_store, load_store
from api.schemas import BuildIndexRequest, FAQRequest

app = FastAPI(title="KALNET AI-3 API")
app.state.vector_store = None

DEFAULT_INDEX_PATH = "data/processed/faiss_index"
TEMP_UPLOAD_DIR = Path("data/interim/uploads")


def _load_existing_store() -> None:
    try:
        app.state.vector_store = load_store(DEFAULT_INDEX_PATH)
    except FileNotFoundError:
        app.state.vector_store = None


@app.on_event("startup")
def startup_event() -> None:
    _load_existing_store()


@app.get("/health")
def health() -> dict[str, str]:
    backend = getattr(app.state.vector_store, "backend", "not_loaded")
    return {"status": "ok", "store_backend": backend}


@app.post("/ai/build-index")
def build_index(payload: BuildIndexRequest) -> dict:
    result = build_store(payload.docs_folder, payload.index_path)
    app.state.vector_store = load_store(payload.index_path)
    return result


@app.post("/ai/faq")
def ask_faq(payload: FAQRequest) -> dict:
    if app.state.vector_store is None:
        try:
            app.state.vector_store = load_store(DEFAULT_INDEX_PATH)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=400,
                detail="Knowledge base not found. Run /ai/build-index first.",
            ) from exc

    return chat_with_bot(
        question=payload.question,
        conversation_history=payload.history,
        store=app.state.vector_store,
    )


@app.post("/ai/summarise")
async def summarise(file: UploadFile = File(...)) -> dict:
    TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = TEMP_UPLOAD_DIR / file.filename

    with target_path.open("wb") as destination:
        shutil.copyfileobj(file.file, destination)

    try:
        return summarise_document(str(target_path))
    finally:
        if target_path.exists():
            target_path.unlink()
