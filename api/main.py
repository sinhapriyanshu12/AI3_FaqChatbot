"""FastAPI entry point.

Owned by Bollam Ankith.
"""

from fastapi import FastAPI, File, UploadFile

from api.schemas import FAQRequest

app = FastAPI(title="KALNET AI-3 API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ai/faq")
def ask_faq(payload: FAQRequest) -> dict:
    return {
        "answer": "Wire this route to agents.faq_bot.chat_with_bot",
        "sources": [],
        "question": payload.question,
    }


@app.post("/ai/summarise")
async def summarise(file: UploadFile | None = File(default=None)) -> dict:
    return {
        "message": "Wire this route to agents.doc_summariser.summarise_document",
        "filename": file.filename if file else None,
    }
