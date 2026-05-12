from __future__ import annotations

from domain.signals.models import GeopoliticalSignal
from agents.exposure_analyzer import analyze_exposure


def test_exposure_increases_with_sanctions():
    profile, exposure = analyze_exposure(
        "Turkey",
        "industrial",
        None,
        None,
        [GeopoliticalSignal(signal_id="s1", category="sanction", country="Turkey", summary="sanction", intensity="critical")],
    )
    assert profile.geopolitical_risk >= 7
    assert exposure.exposure_level == "high"
