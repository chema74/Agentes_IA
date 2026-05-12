from __future__ import annotations

from agents.geopolitical_signal_recorder import record_signals


def test_signal_recorder_detects_sanction():
    signals = record_signals("New sanctions affect export controls for the market.", "Poland")
    assert signals
    assert signals[0].category == "sanction"
