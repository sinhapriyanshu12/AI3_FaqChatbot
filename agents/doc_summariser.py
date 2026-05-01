"""Document summariser for PDF and Word files."""

import json
import os
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.base import get_gemini
from dotenv import load_dotenv

load_dotenv()


def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    return "\n".join([page.get_text() for page in doc])


def extract_text_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Only PDF and DOCX files are supported.")


SUMMARY_PROMPT = """You are a document analysis assistant for a school administrator.
Analyse the document text below and respond ONLY with a JSON object.
No preamble, no markdown, no explanation — just the JSON.

Return this exact structure:
{{
  "title_guess": "your best guess at the document title",
  "summary_bullets": ["bullet 1", "bullet 2", "bullet 3"],
  "key_dates": ["date 1 with context", "date 2 with context"],
  "action_required": true or false,
  "action_description": "what action must be taken, or null if none"
}}

Document text:
{text}"""


def summarise_document(file_path: str) -> dict:
    """Return structured JSON summary of a PDF or Word document."""
    text = extract_text(file_path)

    if not text.strip():
        return {
            "title_guess": "Unknown Document",
            "summary_bullets": ["No readable text found in document."],
            "key_dates": [],
            "action_required": False,
            "action_description": None,
        }

    word_count = len(text.split())

    # Long document — chunk and summarise each part first
    if word_count > 3000:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, chunk_overlap=200
        )
        chunks = splitter.split_text(text)

        llm = get_gemini()
        chunk_summaries = []
        for chunk in chunks:
            response = llm.invoke(
                f"Summarise this section of a school document in 3 sentences:\n{chunk}"
            )
            chunk_summaries.append(response.content)

        combined = "\n".join(chunk_summaries)
    else:
        combined = text

    # Final structured output using Gemini JSON mode
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1,
        generation_config={"response_mime_type": "application/json"},
    )

    prompt = SUMMARY_PROMPT.format(text=combined)
    response = llm.invoke(prompt)
    return json.loads(response.content)