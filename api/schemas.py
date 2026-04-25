"""Pydantic request and response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FAQRequest(BaseModel):
    question: str
    history: list[dict] = Field(default_factory=list)


class FAQResponse(BaseModel):
    answer: str
    sources: list[str]
    matches: list[dict] = Field(default_factory=list)


class BuildIndexRequest(BaseModel):
    docs_folder: str = "data/raw"
    index_path: str = "data/processed/faiss_index"


class BuildIndexResponse(BaseModel):
    chunks_indexed: int
    output_folder: str
    backend: str


class SummariseResponse(BaseModel):
    title_guess: str
    summary_bullets: list[str]
    key_dates: list[str]
    action_required: bool
    action_description: str
