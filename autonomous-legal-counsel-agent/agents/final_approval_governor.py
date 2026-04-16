from __future__ import annotations

from domain.contracts.models import ApprovalRecommendation
from domain.redlines.models import RedlineSuggestion
from domain.risks.models import RiskClause


def decide_approval(risks: list[RiskClause], redlines: list[RedlineSuggestion], breaker_status: str) -> ApprovalRecommendation:
    if breaker_status == "BLOCKED":
        return ApprovalRecommendation(status="BLOCKED", reason="Legal Risk Circuit Breaker activated.")
    if risks or redlines:
        return ApprovalRecommendation(status="NEGOTIABLE", reason="Contract deviates from playbook but has redline path.")
    return ApprovalRecommendation(status="APPROVABLE", reason="Contract aligns with approved positions.")
