from __future__ import annotations

from agents.signal_recorder import capture_signals


def test_signal_recorder_captures_fatigue_signal():
    signals = capture_signals("Hay mucha fatiga en el equipo.")
    assert signals
    assert signals[0].category == "fatigue"
