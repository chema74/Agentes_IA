from __future__ import annotations

from core.safety.protocol import assess_psychological_risk


def test_circuit_breaker_detects_high_risk_language():
    result = assess_psychological_risk("No quiero vivir y estoy pensando en matarme")
    assert result.inferred_risk_level == "high"
    assert result.escalation_status == "HIGH_RISK_ESCALATION"


def test_circuit_breaker_stays_low_without_crisis_markers():
    result = assess_psychological_risk("Hoy estoy triste, cansado y con dudas")
    assert result.inferred_risk_level == "low"
