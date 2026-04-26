"""Document summariser for PDF and Word files."""

from __future__ import annotations
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
import re

from agents.base import split_sentences, tokenize
from data.pipeline.ingest import read_document

DATE_PATTERNS = [
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    re.compile(
        r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
        re.IGNORECASE,
    ),
]
ACTION_TERMS = {
    "submit",
    "respond",
    "complete",
    "pay",
    "attend",
    "upload",
    "verify",
    "report",
    "send",
    "must",
    "required",
    "deadline",
}


def _extract_dates(text: str) -> list[str]:
    found: list[str] = []
    for pattern in DATE_PATTERNS:
        found.extend(match.group(0) for match in pattern.finditer(text))

    seen: set[str] = set()
    unique_dates: list[str] = []
    for item in found:
        lowered = item.lower()
        if lowered not in seen:
            seen.add(lowered)
            unique_dates.append(item)
    return unique_dates[:10]


def _guess_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if len(stripped) >= 6:
            return stripped[:120]
    return path.stem.replace("_", " ").title()


def _rank_sentences(text: str) -> list[str]:
    sentences = split_sentences(text)
    frequencies: dict[str, int] = {}
    for token in tokenize(text):
        frequencies[token] = frequencies.get(token, 0) + 1

    scored: list[tuple[float, str]] = []
    for sentence in sentences:
        sentence_tokens = tokenize(sentence)
        if len(sentence_tokens) < 4:
            continue
        score = sum(frequencies.get(token, 0) for token in sentence_tokens) / len(sentence_tokens)
        if sentence.strip().endswith("?"):
            score *= 0.6
        scored.append((score, sentence))

    return [sentence for _, sentence in sorted(scored, reverse=True)]


def summarise_document(file_path: str) -> dict:
    """Return structured JSON summary output."""
    path = Path(file_path)
    parts = read_document(path)
    text = "\n".join(part["text"] for part in parts if part["text"]).strip()

    if not text:
        return {
            "title_guess": path.stem,
            "summary_bullets": ["No readable text was found in the uploaded document."],
            "key_dates": [],
            "action_required": False,
            "action_description": "",
        }

    ranked_sentences = _rank_sentences(text)
    summary_bullets = ranked_sentences[:5] or [text[:200]]

    action_sentences = [
        sentence
        for sentence in split_sentences(text)
        if any(term in tokenize(sentence) for term in ACTION_TERMS)
    ]
    action_required = bool(action_sentences)
    preferred_actions = [sentence for sentence in action_sentences if not sentence.strip().endswith("?")]
    action_description = preferred_actions[0] if preferred_actions else (action_sentences[0] if action_sentences else "")

    return {
        "title_guess": _guess_title(text, path),
        "summary_bullets": summary_bullets[:5],
        "key_dates": _extract_dates(text),
        "action_required": action_required,
        "action_description": action_description[:300],
    }
