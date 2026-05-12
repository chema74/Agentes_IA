from __future__ import annotations

from core.safety.trade_breaker import evaluate_trade_breaker


def test_breaker_blocks_low_confidence_recommendation():
    result = evaluate_trade_breaker([], [], 0.2, 3)
    assert result.level == 4
