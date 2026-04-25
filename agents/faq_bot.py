"""RAG-based FAQ bot.

Owned by Aditya Lenka.
"""

from typing import Any


REFUSAL_MESSAGE = (
    "I do not have that information — please contact the school office directly."
)


def chat_with_bot(question: str, conversation_history: list[dict[str, Any]]) -> dict[str, Any]:
    """Answer only from retrieved school documents."""
    raise NotImplementedError("Implement RAG retrieval and grounded answer generation.")
