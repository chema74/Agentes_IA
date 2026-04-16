from __future__ import annotations

from services.llm.gemini_client import GEMINI_CLIENT


def test_classifier_detects_nda():
    text = "This Non-Disclosure Agreement protects confidential information exchanged by the parties."
    assert GEMINI_CLIENT.classify_contract_type(text) == "NDA"
