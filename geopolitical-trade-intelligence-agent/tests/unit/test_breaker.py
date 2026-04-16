from __future__ import annotations

from core.safety.trade_breaker import evaluate_trade_breaker
from domain.routes.models import RouteDisruptionAlert
from domain.sanctions.models import SanctionEvent


def test_trade_breaker_blocks_on_sanction():
    result = evaluate_trade_breaker(
        [SanctionEvent(event_id="ev1", category="sanction", impact="high", description="sanction")],
        [],
        0.8,
        5,
    )
    assert result.level == 4
    assert result.human_review_required is True
