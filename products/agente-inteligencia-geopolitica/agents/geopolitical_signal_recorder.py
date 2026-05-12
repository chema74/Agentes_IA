from __future__ import annotations

from uuid import uuid4

from domain.signals.models import GeopoliticalSignal
from services.llm.groq_client import GROQ_CLIENT


def record_signals(signal_text: str, country: str) -> list[GeopoliticalSignal]:
    category, intensity = GROQ_CLIENT.classify_signal(signal_text)
    return [
        GeopoliticalSignal(
            signal_id=f"signal-{uuid4().hex[:10]}",
            category=category,
            country=country,
            summary=signal_text,
            intensity=intensity,
        )
    ]
