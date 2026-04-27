from __future__ import annotations

from services.llm.sambanova_client import SAMBANOVA_CLIENT


def build_explanation(decision: str, failure_reasons: list[str]) -> str:
    return SAMBANOVA_CLIENT.explain_decision(decision=decision, failure_reasons=failure_reasons)
