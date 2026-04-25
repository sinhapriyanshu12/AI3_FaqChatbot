from data.pipeline.ingest import ingest_documents


def test_pipeline_reads_sample_documents() -> None:
    chunks = ingest_documents("data/raw")
    assert chunks
    assert {"source_file", "page_number", "chunk_index", "text"} <= set(chunks[0].keys())
