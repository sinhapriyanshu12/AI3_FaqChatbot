"""Shared vector store helpers."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Any
import json

from agents.base import content_tokens
from data.pipeline.build_kb import build_knowledge_base


@dataclass
class SearchResult:
    text: str
    source_file: str
    source_path: str
    page_number: int | None
    chunk_index: int
    score: float


class BaseStore:
    backend: str

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        raise NotImplementedError


class LexicalStore(BaseStore):
    def __init__(self, payload: dict[str, Any]) -> None:
        self.backend = "lexical"
        self.vocabulary = payload["vocabulary"]
        self.vectors = payload["vectors"]
        self.chunks = payload["chunks"]
        self.token_positions = {token: index for index, token in enumerate(self.vocabulary)}

    def _vectorize(self, text: str) -> list[float]:
        counts = Counter(content_tokens(text))
        vector = [0.0] * len(self.vocabulary)
        norm = sqrt(sum(value * value for value in counts.values())) or 1.0
        for token, count in counts.items():
            position = self.token_positions.get(token)
            if position is not None:
                vector[position] = count / norm
        return vector

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        query_vector = self._vectorize(query)
        scored: list[SearchResult] = []

        for chunk, vector in zip(self.chunks, self.vectors, strict=False):
            score = sum(a * b for a, b in zip(query_vector, vector, strict=False))
            if score <= 0:
                continue
            scored.append(
                SearchResult(
                    text=chunk["text"],
                    source_file=chunk["source_file"],
                    source_path=chunk["source_path"],
                    page_number=chunk["page_number"],
                    chunk_index=chunk["chunk_index"],
                    score=score,
                )
            )

        return sorted(scored, key=lambda item: item.score, reverse=True)[:k]


class FaissStore(BaseStore):
    def __init__(self, index_path: Path) -> None:
        import faiss  # type: ignore
        from sentence_transformers import SentenceTransformer  # type: ignore

        self.backend = "faiss"
        self.index = faiss.read_index(str(index_path / "faiss.index"))
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.chunks = json.loads((index_path / "chunks.json").read_text(encoding="utf-8"))
        self.faiss = faiss

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        vector = self.model.encode([query], convert_to_numpy=True).astype("float32")
        self.faiss.normalize_L2(vector)
        scores, indices = self.index.search(vector, k)
        results: list[SearchResult] = []

        for score, index in zip(scores[0], indices[0], strict=False):
            if index < 0:
                continue
            chunk = self.chunks[int(index)]
            results.append(
                SearchResult(
                    text=chunk["text"],
                    source_file=chunk["source_file"],
                    source_path=chunk["source_path"],
                    page_number=chunk["page_number"],
                    chunk_index=chunk["chunk_index"],
                    score=float(score),
                )
            )

        return results


def build_store(docs_folder: str, index_path: str = "data/processed/faiss_index") -> dict:
    return build_knowledge_base(docs_folder, index_path)


def load_store(index_path: str):
    path = Path(index_path)
    faiss_index = path / "faiss.index"
    lexical_index = path / "lexical_index.json"

    if faiss_index.exists():
        try:
            return FaissStore(path)
        except Exception:
            pass

    if lexical_index.exists():
        payload = json.loads(lexical_index.read_text(encoding="utf-8"))
        return LexicalStore(payload)

    raise FileNotFoundError(
        f"No search index found in {path}. Build one first with build_store()."
    )
