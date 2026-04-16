from __future__ import annotations

from uuid import uuid4

from domain.signals.models import ChangeSignal
from services.llm.groq_client import GROQ_CLIENT


def capture_signals(process_notes: str) -> list[ChangeSignal]:
    items: list[ChangeSignal] = []
    for sentence in [part.strip() for part in process_notes.split(".") if part.strip()]:
        category, intensity = GROQ_CLIENT.classify_signal(sentence)
        items.append(ChangeSignal(signal_id=f"signal-{uuid4().hex[:10]}", category=category, summary=sentence, intensity=intensity, source="direct_input"))
    return items
