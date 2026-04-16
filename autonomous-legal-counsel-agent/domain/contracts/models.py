from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from domain.clauses.models import ClauseMapEntry
from domain.negotiation.models import NegotiationTrack
from domain.redlines.models import RedlineSuggestion
from domain.risks.models import RiskClause


class ApprovalRecommendation(BaseModel):
    status: str
    reason: str


class ContractReview(BaseModel):
    review_id: str
    contract_type: str
    clause_map: list[ClauseMapEntry] = Field(default_factory=list)
    risk_clauses: list[RiskClause] = Field(default_factory=list)
    redline_suggestions: list[RedlineSuggestion] = Field(default_factory=list)
    negotiation_status: str
    approval_recommendation: ApprovalRecommendation
    human_review_required: bool
    legal_notes: list[str] = Field(default_factory=list)
    audit_reference: str
    negotiation_tracks: list[NegotiationTrack] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
