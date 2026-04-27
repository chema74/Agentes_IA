from __future__ import annotations

from uuid import uuid4

from domain.integrity.models import IntegrityAlert


def build_integrity_alert(student_id: str, evaluation_event_id: str, level: int, incoherences: list[str], confidence_score: float, breaker: bool) -> IntegrityAlert | None:
    if level == 1 and not incoherences:
        return None
    return IntegrityAlert(
        id=f"alert-{uuid4().hex[:12]}",
        student_id=student_id,
        evaluation_event_id=evaluation_event_id,
        signal_level=level,
        signal_type="integrity_signal_cluster",
        description="; ".join(incoherences) if incoherences else "Observacion de seguimiento sin anomalia grave.",
        supporting_evidence_refs=incoherences,
        confidence_score=round(confidence_score, 2),
        circuit_breaker_triggered=breaker,
    )
