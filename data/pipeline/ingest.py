"""Document ingestion pipeline.

Reads common document types, chunks text, and attaches source metadata.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
import json

from agents.base import normalise_text

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SUPPORTED_SUFFIXES = {".pdf", ".docx", ".txt", ".md"}


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[str]:
    clean = normalise_text(text)
    if not clean:
        return []

    paragraphs = [paragraph.strip() for paragraph in clean.split("\n\n") if paragraph.strip()]
    if len(paragraphs) > 1:
        paragraph_chunks = [paragraph for paragraph in paragraphs if paragraph]
        if paragraph_chunks:
            return paragraph_chunks

    chunks: list[str] = []
    start = 0
    length = len(clean)

    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            split_at = clean.rfind(" ", start, end)
            if split_at > start + 200:
                end = split_at

        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break
        start = max(end - chunk_overlap, 0)

    return chunks


def _read_pdf(path: Path) -> list[dict]:
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required to read PDF files.") from exc

    pages: list[dict] = []
    with fitz.open(path) as document:
        for page_index, page in enumerate(document, start=1):
            pages.append(
                {
                    "page_number": page_index,
                    "text": normalise_text(page.get_text("text")),
                }
            )
    return pages


def _read_docx(path: Path) -> list[dict]:
    try:
        from docx import Document  # type: ignore
    except ImportError as exc:
        raise RuntimeError("python-docx is required to read Word files.") from exc

    document = Document(path)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    return [{"page_number": None, "text": normalise_text(text)}]


def _read_text(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    return [{"page_number": None, "text": normalise_text(text)}]


def read_document(path: str | Path) -> list[dict]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return _read_pdf(file_path)
    if suffix == ".docx":
        return _read_docx(file_path)
    if suffix in {".txt", ".md"}:
        return _read_text(file_path)

    raise ValueError(f"Unsupported file type: {file_path.suffix}")


def iter_supported_files(input_folder: str | Path) -> Iterable[Path]:
    folder = Path(input_folder)
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path


def ingest_documents(input_folder: str) -> list[dict]:
    """Read files, extract text, chunk them, and attach metadata."""
    chunks: list[dict] = []

    for file_path in iter_supported_files(input_folder):
        pages = read_document(file_path)
        chunk_index = 0
        for page in pages:
            for chunk in _chunk_text(page["text"]):
                chunks.append(
                    {
                        "text": chunk,
                        "source_file": file_path.name,
                        "source_path": str(file_path),
                        "page_number": page["page_number"],
                        "chunk_index": chunk_index,
                    }
                )
                chunk_index += 1

    return chunks


def save_chunks(chunks: list[dict], output_file: str | Path) -> None:
    Path(output_file).write_text(json.dumps(chunks, indent=2), encoding="utf-8")
