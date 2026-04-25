from agents.doc_summariser import summarise_document


def test_doc_summariser_extracts_dates() -> None:
    summary = summarise_document("data/raw/admissions_faq.txt")
    assert summary["title_guess"]
    assert summary["summary_bullets"]
    assert any("2026" in item for item in summary["key_dates"])
