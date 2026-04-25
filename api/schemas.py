"""Pydantic request and response models."""

from pydantic import BaseModel


class FAQRequest(BaseModel):
    question: str
    history: list[dict] = []


class FAQResponse(BaseModel):
    answer: str
    sources: list[str]


class SummariseResponse(BaseModel):
    title_guess: str
    summary_bullets: list[str]
    key_dates: list[str]
    action_required: bool
    action_description: str
