# KALNET AI-3

Defined working structure for the `AI-3 — FAQ Chatbot + Document Summariser` project, organized so the team can open it in VS Code and start building immediately.

## Project Goal

Build two AI features for the student portal:

1. A RAG-based FAQ chatbot that answers only from approved school documents.
2. A document summariser that extracts key bullets, dates, and required actions from uploaded files.

## Recommended Workflow

1. `agents/` contains the AI logic owned by the AI/LLM team.
2. `data/pipeline/` contains ingestion and FAISS knowledge-base building.
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
2. Run ingestion and FAISS build
3. Build and test the FAQ bot
4. Build and test the summariser
5. Expose both via FastAPI
6. Integrate the React widget into the portal

## Important Rule

The FAQ bot must never answer outside the provided school documents. If the answer is not found, it should refuse gracefully.
