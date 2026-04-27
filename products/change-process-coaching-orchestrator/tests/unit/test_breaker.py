from __future__ import annotations

from core.safety.change_breaker import evaluate_change_breaker
from domain.friction.models import AdoptionBlocker, FrictionAssessment
from domain.progress.models import ChangeFatigueAlert
from domain.resistance.models import ResistanceProfile


def test_breaker_escalates_level_four_on_fatigue_and_blocker():
    result = evaluate_change_breaker(
        FrictionAssessment(level="high", confidence=0.9, process_status="comprometido"),
        ResistanceProfile(resistance_type="overload", intensity="high", rationale="test"),
        [AdoptionBlocker(blocker="execution_block", impact="critical", recommended_response="remove")],
        ChangeFatigueAlert(level="high", evidence="fatigue"),
    )
    assert result.level == 4
    assert result.human_review_required is True
    assert result.automation_stop is True
