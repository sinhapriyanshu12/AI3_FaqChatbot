# AI3 — KALNET School FAQ Chatbot + Document Summariser

A two-feature AI system built for the KALNET school portal.

## Features

**Feature 1 — FAQ Chatbot**
Students ask questions about admissions, fees, or school rules. The bot retrieves answers from uploaded school PDF documents using RAG (Retrieval Augmented Generation) and cites the source file.

**Feature 2 — Document Summariser**
Upload any school PDF or DOCX (circulars, policy documents). The system returns a structured JSON with title, bullet-point summary, key dates, and whether action is required.

## Tech Stack

- Python 3.11
- LangChain + LangChain Community
- FAISS (vector store)
- HuggingFace Sentence Transformers (embeddings)
- Google Gemini 1.5 Flash (LLM — free API)
- FastAPI + Uvicorn (backend)
- PyMuPDF (PDF reading)
- React + TypeScript (frontend widget)

## Project Structure

```
AI3_FaqChatbot/
├── agents/
│   ├── base.py              # Gemini LLM initialisation
│   ├── vector_store.py      # FAISS build and load
│   ├── faq_bot.py           # RAG chain for FAQ
│   └── doc_summariser.py    # Document summarisation
├── data/
│   ├── raw/                 # Put school PDFs here
│   ├── pipeline/
│   │   ├── ingest.py        # Load and chunk documents
│   │   └── build_kb.py      # Build FAISS index
│   └── processed/
│       └── faiss_index/     # Auto-generated
├── api/
│   └── main.py              # FastAPI endpoints
├── frontend/
│   └── components/
│       └── FAQChatWidget.tsx
├── tests/
│   └── test_search.py
├── requirements.txt
└── .env.example
```

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/sinhapriyanshu12/AI3_FaqChatbot.git
cd AI3_FaqChatbot
```

### 2. Create virtual environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
# Get free key at: https://aistudio.google.com/app/apikey
```

### 5. Add school documents
Place PDF files in `data/raw/` folder.

### 6. Build the knowledge base
```bash
python data/pipeline/build_kb.py
```

### 7. Run the API server
```bash
uvicorn api.main:app --reload --port 8000
```

### 8. Test the FAQ endpoint
```bash
curl -X POST http://localhost:8000/ai/faq \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the tuition fee for Class 9?"}'
```

## Team

| Person | Role | Files |
|--------|------|-------|
| Priyanshu | Team Lead | agents/base.py, agents/vector_store.py |
| Aditya Lenka | LLM Engineer 1 | agents/faq_bot.py, data/raw/*.pdf |
| Aashrith Vathsal | LLM Engineer 2 | agents/doc_summariser.py |
| Chirag Jain | Data Engineer | data/pipeline/ingest.py, build_kb.py, tests/ |
| Bollam Ankith | API + Frontend | api/main.py, frontend/FAQChatWidget.tsx |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| POST | /ai/faq | Ask a question to the FAQ bot |
| POST | /ai/summarise | Upload a document to summarise |
