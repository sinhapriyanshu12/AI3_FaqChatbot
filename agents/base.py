"""Shared model initialization utilities.

Owned by Priyanshu.
"""

from dataclasses import dataclass
import os


@dataclass
class GeminiConfig:
    api_key: str
    model_name: str = "gemini-1.5-flash"


def load_gemini_config() -> GeminiConfig:
    api_key = os.getenv("GEMINI_API_KEY", "")
    return GeminiConfig(api_key=api_key)
