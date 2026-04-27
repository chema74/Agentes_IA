from __future__ import annotations

from core.safety.legal_risk_breaker import evaluate_legal_breaker
from domain.risks.models import RiskClause


def test_never_approvable_with_critical_data_transfer():
    risk = RiskClause(
        risk_clause_id="risk-2",
        clause_id="cl-2",
        category="data_transfer",
        severity="critical",
        playbook_rule_id="rule-data_transfer",
        deviation_type="incompatible_transfer",
        risk_reason="Outside EU transfer",
        recommended_action="Use SCC",
        human_review_required=True,
    )
    result = evaluate_legal_breaker([risk])
    assert result.status == "BLOCKED"
