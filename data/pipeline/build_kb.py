"""Knowledge-base builder.

Builds a saved search index using FAISS when available, and always stores a
portable lexical index so the project still runs in fully offline setups.
"""

from __future__ import annotations

from collections import Counter
from math import sqrt
import json

from agents.base import content_tokens, ensure_directory
from data.pipeline.ingest import ingest_documents


def _build_lexical_vectors(chunks: list[dict]) -> tuple[list[str], list[list[float]]]:
    vocabulary_counter: Counter[str] = Counter()
    tokenized_chunks: list[list[str]] = []

    for chunk in chunks:
        tokens = content_tokens(chunk["text"])
        tokenized_chunks.append(tokens)
        vocabulary_counter.update(set(tokens))

    vocabulary = sorted(vocabulary_counter)
    token_positions = {token: index for index, token in enumerate(vocabulary)}
    vectors: list[list[float]] = []

    for tokens in tokenized_chunks:
        counts = Counter(tokens)
        vector = [0.0] * len(vocabulary)
        norm = sqrt(sum(value * value for value in counts.values())) or 1.0
        for token, count in counts.items():
            position = token_positions[token]
            vector[position] = count / norm
        vectors.append(vector)

    return vocabulary, vectors


def build_knowledge_base(input_folder: str, output_folder: str) -> dict:
    """Embed chunks and save the search index."""
    chunks = ingest_documents(input_folder)
    if not chunks:
        raise ValueError(f"No supported documents found in {input_folder}")

    output_dir = ensure_directory(output_folder)
    vocabulary, lexical_vectors = _build_lexical_vectors(chunks)

    lexical_payload = {
        "backend": "lexical",
        "vocabulary": vocabulary,
        "vectors": lexical_vectors,
        "chunks": chunks,
    }
    (output_dir / "lexical_index.json").write_text(
        json.dumps(lexical_payload, indent=2),
        encoding="utf-8",
    )

    backend = "lexical"
    try:
        import faiss  # type: ignore
        from sentence_transformers import SentenceTransformer  # type: ignore

        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        embeddings = model.encode([chunk["text"] for chunk in chunks], convert_to_numpy=True)
        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, str(output_dir / "faiss.index"))
        (output_dir / "chunks.json").write_text(json.dumps(chunks, indent=2), encoding="utf-8")
        backend = "faiss"
    except Exception:
        backend = "lexical"

    return {
        "chunks_indexed": len(chunks),
        "output_folder": str(output_dir),
        "backend": backend,
    }
