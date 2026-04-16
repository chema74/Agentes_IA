from __future__ import annotations

from pydantic import BaseModel


class RiskClause(BaseModel):
    risk_clause_id: str
    clause_id: str
    category: str
    severity: str
    playbook_rule_id: str
    deviation_type: str
    risk_reason: str
    recommended_action: str
    human_review_required: bool
