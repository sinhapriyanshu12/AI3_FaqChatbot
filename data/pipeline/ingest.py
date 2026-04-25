"""Document ingestion pipeline.

Owned by Chirag Jain.
"""


def ingest_documents(input_folder: str) -> list[dict]:
    """Read files, extract text, chunk them, and attach metadata."""
    raise NotImplementedError("Implement PDF and Word ingestion with chunk metadata.")
