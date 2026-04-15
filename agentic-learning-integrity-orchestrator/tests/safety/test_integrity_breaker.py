from __future__ import annotations

from core.safety.integrity_breaker import evaluate_integrity_level


def test_circuit_breaker_level_four_when_no_evidence_or_low_confidence():
    result = evaluate_integrity_level(["salto_brusco_de_complejidad"], 0.2, 0)
    assert result.level == 4
    assert result.circuit_breaker_triggered is True


def test_level_three_when_multiple_incoherences_converge():
    result = evaluate_integrity_level(["a", "b", "c"], 0.7, 2)
    assert result.level == 3
