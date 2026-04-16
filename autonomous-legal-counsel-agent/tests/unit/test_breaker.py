from __future__ import annotations

from core.safety.legal_risk_breaker import evaluate_legal_breaker
from domain.risks.models import RiskClause


def test_legal_breaker_blocks_critical_clause():
    risk = RiskClause(
        risk_clause_id="risk-1",
        clause_id="cl-1",
        category="jurisdiction",
        severity="critical",
        playbook_rule_id="rule-jurisdiction",
        deviation_type="forbidden_forum",
        risk_reason="Forbidden forum",
        recommended_action="Replace",
        human_review_required=True,
    )
    result = evaluate_legal_breaker([risk])
    assert result.status == "BLOCKED"
    assert "UNACCEPTABLE_JURISDICTION" in result.reason_codes
