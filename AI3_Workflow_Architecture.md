# AI-3 Workflow Architecture

## 1. Project Objective

The AI-3 system for KALNET has two deliverables that work together inside the student portal:

1. A FAQ chatbot that answers only from approved school documents.
2. A document summariser that extracts key points, important dates, and required actions from uploaded files.

The overall business goal is to provide a reliable school-assistant experience inside the portal, improve information access for students and administrators, and increase the value of the platform.

## 2. High-Level System Architecture

The system is made of five connected layers:

1. Document Layer
School documents such as admissions FAQs, fee structures, school rules, circulars, CBSE notices, and holiday lists are created or uploaded.

2. Knowledge Processing Layer
Documents are ingested, text is extracted, content is chunked, metadata is attached, embeddings are generated, and a FAISS index is built.

3. AI Service Layer
Two AI services sit on top of the processed data:
- FAQ Bot service for document-grounded question answering
- Document Summariser service for structured summaries from uploaded files

4. API Layer
FastAPI exposes both capabilities through backend endpoints.

5. UI and Portal Integration Layer
A React chatbot widget is embedded into the FS-2 student portal so users can ask questions directly from the portal interface.

## 3. End-to-End Workflow

### A. FAQ Chatbot Workflow

1. School documents are prepared as the source of truth.
2. The ingestion pipeline reads PDF and Word documents.
3. Text is split into chunks with metadata such as source file, page number, and chunk index.
4. Each chunk is converted into embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
5. The embedded chunks are stored in a FAISS vector index.
6. At API startup, the FAISS vector store is loaded once into memory.
7. A user opens the student portal and asks a question in the floating chat widget.
8. The widget sends the question and conversation history to `POST /ai/faq`.
9. The FAQ bot retrieves the most relevant chunks from FAISS.
10. Gemini receives the retrieved context plus a strict instruction to answer only from provided school documents.
11. The model returns:
- An answer grounded in the documents
- A refusal if the answer is not present
- Source citations for traceability
12. The API sends the answer back to the widget.
13. The widget displays the answer, typing state, and source citation.

### B. Document Summariser Workflow

1. A principal, admin, or user uploads a PDF or Word file.
2. The file is sent to `POST /ai/summarise`.
3. The summariser reads the file using:
- PyMuPDF for PDFs
- python-docx for Word documents
4. If the document is short, it can be processed directly.
5. If the document is longer than 3000 words, it is chunked using `RecursiveCharacterTextSplitter`.
6. A map-reduce summarisation pattern is applied to preserve coverage across the whole document.
7. Gemini is called with `response_mime_type=application/json`.
8. The output is returned in a strict JSON structure:
- `title_guess`
- `summary_bullets`
- `key_dates`
- `action_required`
- `action_description`
9. The API returns the structured summary to the UI or consuming system.

## 4. Architecture by Component

### 4.1 Source Documents

These are the foundation of the system. The chatbot must not answer beyond them.

Core expected documents:
- `admissions_faq.pdf`
- `fee_structure.pdf`
- `school_rules.pdf`
- real-style circulars and notices for summarisation tests

Why this matters:
- The FAQ bot is only as trustworthy as the documents it retrieves from.
- The summariser quality depends on realistic test files that represent actual school operations.

### 4.2 Ingestion and Knowledge Base

This component converts raw files into searchable knowledge.

Main responsibilities:
- Read PDFs and Word files
- Extract text
- Split text into chunks using `chunk_size=800` and `chunk_overlap=100`
- Add metadata:
  - `source_file`
  - `page_number`
  - `chunk_index`
- Generate embeddings
- Store vectors in FAISS

Why this matters:
- Good chunking improves retrieval quality.
- Metadata makes source citation possible.
- A stable vector index is the backbone of the chatbot.

### 4.3 FAQ Bot / RAG Layer

This is the retrieval-augmented generation engine.

Responsibilities:
- Accept a question and conversation history
- Retrieve relevant document chunks from FAISS
- Pass only the relevant context into Gemini
- Enforce refusal behavior when information is missing
- Return answer plus source references

Critical rule:
- The bot must never hallucinate or invent school information.

Why this matters:
- In a school context, incorrect information about fees, admissions, or rules can create operational and reputational problems.

### 4.4 Summariser Layer

This component turns long documents into structured decisions and key takeaways.

Responsibilities:
- Read uploaded files
- Detect and handle long documents
- Create concise bullets
- Extract dates
- Detect whether action is required
- Describe what action is required

Why this matters:
- Administrators need actionable summaries, not just compressed text.
- Structured JSON makes the output reusable in dashboards, notifications, or workflow automation.

### 4.5 FastAPI Backend

This layer exposes the AI capabilities to the portal.

Endpoints:
- `POST /ai/faq`
- `POST /ai/summarise`

Responsibilities:
- Validate inputs
- Load vector store once at startup
- Call the correct agent
- Return clean responses to frontend systems

Why this matters:
- This is the bridge between AI logic and the product UI.
- Startup loading improves performance and avoids repeated index loading in route handlers.

### 4.6 React Widget and Portal Integration

This is the user-facing delivery layer.

Responsibilities:
- Floating chat button in portal
- Message thread UI
- Typing indicator
- Show source citation below each answer
- Send chat history for multi-turn continuity
- Integrate inside the FS-2 student portal layout

Why this matters:
- Even a good backend fails if the UI is confusing.
- The widget is the feature users actually experience.

## 5. Role-by-Role Detailed Responsibility

## Priyanshu - Team Lead

### Primary ownership
- Core architecture setup
- Shared AI foundation files
- Team coordination
- Integration coordination
- Quality gate through PR review

### Technical work
- Create `/agents/base.py` with Gemini initialization
- Create `/agents/vector_store.py`
- Implement:
  - `build_store(docs_folder)`
  - `load_store(index_path)`
- Set the standard pattern for how other AI modules connect to Gemini and vector storage

### Coordination work
- Run daily standups
- Track blockers
- Review team pull requests
- Prepare evening progress report for CTO
- Coordinate Week 4 integration with FS-2 Team Lead Aditya Bibhishan Jagtap

### Why Priyanshu's role is critical
- He is the technical and delivery anchor of the squad.
- If the base architecture is inconsistent, everyone builds on different assumptions.
- If PR review is weak, integration issues appear late in Week 4 or Week 5.

### Expected outputs
- Shared base agent file
- Shared vector store utility
- Reviewed PRs
- Daily alignment across team members
- Smooth embed into student portal

## Aditya Lenka - LLM Engineer 1

### Primary ownership
- FAQ bot intelligence
- RAG chain behavior
- School FAQ data preparation

### Technical work
- Build `/agents/faq_bot.py`
- Implement the RAG chain using the FAISS index produced by the data pipeline
- Build `chat_with_bot(question: str, conversation_history: list)`
- Support multi-turn context
- Enforce the non-negotiable prompt rule:
  - answer only from provided school documents
  - refuse gracefully if answer is not found

### Content preparation work
- Create 3 foundational school documents:
  - `admissions_faq.pdf`
  - `fee_structure.pdf`
  - `school_rules.pdf`

### Testing work
- 10 in-document questions must answer accurately
- 5 out-of-document questions must refuse correctly

### Why Aditya's role is critical
- He directly controls whether the chatbot feels intelligent, safe, and useful.
- The quality of his source documents affects downstream retrieval quality.
- He defines the behavior users trust when asking sensitive school questions.

### Expected outputs
- Working RAG chatbot logic
- Realistic school knowledge documents
- Accurate answers with graceful refusal behavior

## V. Aashrith Vathsal - LLM Engineer 2

### Primary ownership
- Document summarisation engine
- Structured extraction from school and government notices

### Technical work
- Build `/agents/doc_summariser.py`
- Read PDF with PyMuPDF
- Read Word with python-docx
- For large documents, chunk using:
  - `chunk_size=2000`
  - `overlap=200`
- Apply map-reduce summarisation
- Force JSON output through Gemini

### Output contract
- `title_guess`
- `summary_bullets`
- `key_dates`
- `action_required`
- `action_description`

### Testing work
- Test on 5 realistic document types:
  - school circular
  - CBSE schedule
  - fee revision notice
  - RTE order
  - holiday list

### Why Aashrith's role is critical
- He owns the second major product feature.
- The summariser must do more than shorten text; it must extract decisions and deadlines.
- Structured outputs create long-term product value because they are machine-consumable.

### Expected outputs
- Reliable document summariser
- Consistent structured JSON output
- Strong handling of long and formal documents

## Chirag Jain - Data Engineer

### Primary ownership
- Document ingestion pipeline
- Chunking strategy
- Metadata design
- FAISS index build process

### Technical work
- Build `/data/pipeline/ingest.py`
- Build `/data/pipeline/build_kb.py`
- Extract text from PDF and Word files
- Chunk documents with:
  - `chunk_size=800`
  - `chunk_overlap=100`
- Add metadata:
  - `source_file`
  - `page_number`
  - `chunk_index`
- Create embeddings with `all-MiniLM-L6-v2`
- Save FAISS index to `data/processed/faiss_index/`

### Validation work
- Test `search(query, k=3)` with 10 queries
- Verify the returned chunks are actually relevant

### Why Chirag's role is critical
- Retrieval quality depends heavily on ingestion quality.
- If chunking is poor, the chatbot may miss the right answer even if the document contains it.
- If metadata is incomplete, source citation becomes unreliable.

### Expected outputs
- Clean ingestion pipeline
- Searchable vector knowledge base
- Retrieval test evidence showing relevant chunk matches

## Bollam Ankith - API Dev + QA

### Primary ownership
- API exposure
- Frontend widget
- QA scoring and validation

### Technical work
- Build FastAPI endpoints:
  - `POST /ai/faq`
  - `POST /ai/summarise`
- Ensure FAISS index loads once at app startup
- Build `FAQChatWidget.tsx`
- Add floating chat button, message thread, typing indicator, and source citation display
- Share widget with FS-2 Team Lead for portal integration

### QA work
- Test FAQ bot with 30 questions
- Score responses from 1 to 5
- Target average score of 4.0 or above
- Document findings in `/docs/faq_evaluation.md`

### Why Ankith's role is critical
- He connects the AI engine to the actual product experience.
- He also owns the evidence that the system is good enough to demo.
- Without his API and QA work, the project may function in isolation but not in the portal.

### Expected outputs
- Stable AI API
- Usable portal chat widget
- Evaluation report proving quality

## 6. How Work Flows Between People

The team does not work in isolation. Each role is part of a dependency chain.

### Dependency flow

1. Aditya Lenka creates the initial school documents.
2. Chirag Jain ingests those documents and builds the FAISS knowledge base.
3. Priyanshu provides the common AI base and vector store utilities that standardize implementation.
4. Aditya Lenka builds the FAQ bot using Chirag's vector store output and Priyanshu's shared base architecture.
5. Aashrith Vathsal works in parallel on the summariser because his feature is less dependent on the FAQ knowledge base.
6. Bollam Ankith exposes both features through FastAPI.
7. Bollam Ankith builds the chat widget and shares it with the FS-2 team.
8. Priyanshu coordinates final portal embedding and cross-team integration.
9. QA and demo validation happen before the Week 5 live demo.

## 7. Suggested Operating Model by Week

### Week 1
- Aditya prepares realistic source documents
- Priyanshu sets up shared architecture files
- Chirag starts ingestion and index build

### Week 2
- Chirag validates retrieval quality
- Aditya starts FAQ bot after retrieval proves useful
- Priyanshu reviews design consistency

### Week 3
- Aditya completes RAG workflow
- Aashrith completes summariser core logic
- Priyanshu reviews both AI modules

### Week 4
- Ankith exposes APIs
- Ankith builds and shares widget
- Priyanshu coordinates with FS-2 lead for embed

### Week 5
- Full integration testing
- 30-question QA evaluation
- Source citation validation
- Demo readiness and squad presentation

## 8. Governance and Communication Structure

### Daily communication
- Every intern reports by 9:30 AM
- Priyanshu compiles the squad status
- CTO receives the summary by 10:00 AM

### Escalation rule
- If blocked for more than 2 hours, escalate immediately to the Group Leader

### Code governance
- All work goes through pull request review
- No direct push to main

### Demo governance
- Every Friday from 4 to 5 PM each person demos their feature in browser

This governance model is important because it reduces silent delays, catches integration risk early, and keeps accountability visible across the whole squad.

## 9. Risks and Failure Points

### Risk 1: Weak sample documents
If the source documents are unrealistic or incomplete, the chatbot will appear weak even if the code is correct.

### Risk 2: Poor chunking or metadata
If ingestion is weak, retrieval quality drops and source citations become unreliable.

### Risk 3: Hallucinated answers
If the prompt and retrieval controls are weak, the bot may invent policy or fee details.

### Risk 4: Startup inefficiency
If FAISS loads on every request instead of once at startup, response time will degrade.

### Risk 5: Late integration with FS-2
If widget sharing and portal embedding happen too late, demo readiness is threatened.

### Risk 6: Summariser output inconsistency
If JSON output is not enforced, frontend and downstream consumers may break.

## 10. Definition of Success

The project is successful when:

1. The FAQ chatbot answers only from school documents.
2. Every answer includes correct source citation.
3. Missing information is refused gracefully.
4. The summariser produces structured, actionable summaries.
5. Both features are accessible through FastAPI.
6. The chatbot widget is embedded inside the FS-2 student portal.
7. QA score reaches at least 4.0 average over 30 questions.
8. The complete flow works live during the Week 5 demo.

## 11. One-Line Summary

This project works as a coordinated pipeline where documents become a searchable knowledge base, AI agents turn that knowledge into answers and summaries, APIs expose the intelligence, the widget delivers it inside the portal, and each team member owns one essential stage of that delivery chain.
