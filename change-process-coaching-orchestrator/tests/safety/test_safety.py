from __future__ import annotations

from core.safety.change_breaker import evaluate_change_breaker
from domain.friction.models import FrictionAssessment
from domain.progress.models import ChangeFatigueAlert
from domain.resistance.models import ResistanceProfile


def test_never_emit_strong_automation_on_low_confidence():
    result = evaluate_change_breaker(
        FrictionAssessment(level="medium", confidence=0.2, process_status="en_friccion"),
        ResistanceProfile(resistance_type="legitimate_concern", intensity="medium", rationale="test"),
        [],
        ChangeFatigueAlert(level="low", evidence="none"),
    )
    assert result.level == 4
    assert result.automation_stop is True
