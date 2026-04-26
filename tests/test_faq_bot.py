from agents.faq_bot import REFUSAL_MESSAGE, chat_with_bot


def test_faq_answers_from_documents(built_store) -> None:
    response = chat_with_bot("What is the tuition fee for Class 9?", [], store=built_store)
    assert "18,000" in response["answer"]
    assert response["sources"]


def test_faq_refuses_out_of_scope_question(built_store) -> None:
    response = chat_with_bot("Who is the captain of the football team?", [], store=built_store)
    assert response["answer"] == REFUSAL_MESSAGE
