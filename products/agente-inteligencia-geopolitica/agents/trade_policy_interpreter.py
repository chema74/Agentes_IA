from __future__ import annotations

from uuid import uuid4

from domain.sanctions.models import SanctionEvent
from domain.signals.models import GeopoliticalSignal


def interpret_trade_policy(signals: list[GeopoliticalSignal]) -> list[SanctionEvent]:
    events: list[SanctionEvent] = []
    for signal in signals:
        if signal.category in {"sanction", "trade_policy"}:
            events.append(
                SanctionEvent(
                    event_id=f"sanction-{uuid4().hex[:10]}",
                    category=signal.category,
                    impact="high" if signal.intensity in {"high", "critical"} else "moderate",
                    description=signal.summary,
                )
            )
    return events
