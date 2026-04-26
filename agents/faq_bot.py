"""RAG-style FAQ bot with grounded extractive answers."""

from __future__ import annotations

from typing import Any

from agents.base import content_tokens, split_sentences, tokenize
from agents.vector_store import BaseStore, load_store


REFUSAL_MESSAGE = "I do not have that information - please contact the school office directly."


def _score_sentence(sentence: str, query_tokens: set[str]) -> float:
    sentence_tokens = set(content_tokens(sentence))
    if not sentence_tokens:
        return 0.0
    overlap = len(query_tokens & sentence_tokens)
    score = overlap / len(query_tokens or {"_"})
    if sentence.strip().endswith("?"):
        score *= 0.6
    return score


def _extract_answer(question: str, context_blocks: list[str]) -> str:
    query_tokens = set(content_tokens(question))
    scored_sentences: list[tuple[float, str]] = []

    for block in context_blocks:
        for sentence in split_sentences(block):
            score = _score_sentence(sentence, query_tokens)
            if score > 0:
                scored_sentences.append((score, sentence))

    if not scored_sentences:
        return REFUSAL_MESSAGE

    ranked = [sentence for _, sentence in sorted(scored_sentences, reverse=True)]
    preferred = [sentence for sentence in ranked if not sentence.strip().endswith("?")]
    answer = (preferred[0] if preferred else ranked[0]).strip()
    return answer or REFUSAL_MESSAGE


def chat_with_bot(
    question: str,
    conversation_history: list[dict[str, Any]],
    store: BaseStore | None = None,
    k: int = 3,
) -> dict[str, Any]:
    """Answer only from retrieved school documents."""
    del conversation_history
    search_store = store or load_store("data/processed/faiss_index")
    results = search_store.search(question, k=k)

    if not results:
        return {"answer": REFUSAL_MESSAGE, "sources": [], "matches": []}

    top_score = results[0].score
    if top_score < 0.12:
        return {"answer": REFUSAL_MESSAGE, "sources": [], "matches": []}

    answer = _extract_answer(question, [result.text for result in results])
    if answer == REFUSAL_MESSAGE:
        return {"answer": answer, "sources": [], "matches": []}

    sources = []
    for result in results:
        suffix = f" (page {result.page_number})" if result.page_number else ""
        source_label = f"{result.source_file}{suffix}"
        if source_label not in sources:
            sources.append(source_label)

    matches = [
        {
            "source_file": result.source_file,
            "page_number": result.page_number,
            "chunk_index": result.chunk_index,
            "score": round(result.score, 4),
        }
        for result in results
    ]

    return {"answer": answer, "sources": sources, "matches": matches}
