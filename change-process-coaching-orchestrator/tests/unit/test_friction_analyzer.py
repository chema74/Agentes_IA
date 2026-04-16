from __future__ import annotations

from agents.friction_analyzer import analyze_friction
from domain.signals.models import ChangeSignal


def test_friction_analyzer_detects_high_friction():
    resistance, blockers, friction, fatigue = analyze_friction(
        [
            ChangeSignal(signal_id="s1", category="fatigue", summary="fatiga", intensity="high", source="test"),
            ChangeSignal(signal_id="s2", category="execution_block", summary="bloqueo", intensity="high", source="test"),
        ]
    )
    assert friction.level == "high"
    assert blockers
    assert fatigue.level == "high"
    assert resistance.intensity == "high"
    assert friction.discourse_execution_gap in {"medium", "high"}
