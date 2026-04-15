from __future__ import annotations

from core.safety.protocol import SafetyAssessment, assess_psychological_risk


def run_circuit_breaker(text: str) -> SafetyAssessment:
    return assess_psychological_risk(text)
