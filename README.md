# KALNET AI-3

Defined working structure for the `AI-3 - FAQ Chatbot + Document Summariser` project, organized so the team can open it in VS Code and start building immediately.

## Project Goal

Build two AI features for the student portal:

1. A RAG-based FAQ chatbot that answers only from approved school documents.
2. A document summariser that extracts key bullets, dates, and required actions from uploaded files.

## Recommended Workflow

1. `agents/` contains the AI logic owned by the AI/LLM team.
2. `data/pipeline/` contains ingestion and search-index building.
3. `api/` exposes the features through FastAPI.
4. `frontend/` contains the React widget for embedding into the portal.
5. `docs/` stores evaluation, architecture, and delivery notes.
6. `tests/` contains retrieval, chatbot, summariser, and API tests.

## Team Ownership

- `Priyanshu`: `agents/base.py`, `agents/vector_store.py`, architecture review, integration coordination
- `Aditya Lenka`: `agents/faq_bot.py`, sample documents in `data/raw/`
- `V. Aashrith Vathsal`: `agents/doc_summariser.py`
- `Chirag Jain`: `data/pipeline/ingest.py`, `data/pipeline/build_kb.py`
- `Bollam Ankith`: `api/`, `frontend/`, `docs/faq_evaluation.md`

## Suggested Run Order

1. Add sample documents to `data/raw/`
2. Run ingestion and search-index build
3. Run the FastAPI app
4. Build and test the FAQ bot
5. Build and test the summariser
6. Integrate the React widget into the portal

## Important Rule

The FAQ bot must never answer outside the provided school documents. If the answer is not found, it should refuse gracefully.

## Run Commands

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API:

```powershell
uvicorn api.main:app --reload
```

Build the index:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/ai/build-index" -ContentType "application/json" -Body "{}"
```

Ask the FAQ bot:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/ai/faq" -ContentType "application/json" -Body '{"question":"What is the tuition fee for Class 9?","history":[]}'
```

Run tests:

```powershell
pytest
```
