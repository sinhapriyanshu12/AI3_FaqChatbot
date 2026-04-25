"""Shared model and text utilities.

The project prefers free and local-first building blocks so the app remains
usable even when external model APIs are unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "by",
    "do",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "was",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
}


@dataclass
class GeminiConfig:
    api_key: str
    model_name: str = "gemini-1.5-flash"


def load_gemini_config() -> GeminiConfig:
    api_key = os.getenv("GEMINI_API_KEY", "")
    return GeminiConfig(api_key=api_key)


def normalise_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def content_tokens(text: str) -> list[str]:
    return [token for token in tokenize(text) if token not in STOPWORDS]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", normalise_text(text))
    return [part.strip() for part in parts if part.strip()]


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
