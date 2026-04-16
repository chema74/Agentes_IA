from __future__ import annotations

from services.llm.gemini_client import GEMINI_CLIENT


def classify_contract(text: str) -> str:
    return GEMINI_CLIENT.classify_contract_type(text)
