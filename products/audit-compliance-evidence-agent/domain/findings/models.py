from __future__ import annotations

from datetime import datetime, UTC

from pydantic import BaseModel, Field


class FindingEvidenceLink(BaseModel):
    id: str
    finding_id: str
    evidence_id: str
    relationship_type: str
    commentary: str = ""


class Finding(BaseModel):
    id: str
    scope_id: str
    control_id: str
    title: str
    severity: str
    explanation: str
    confidence: float
    preliminary_recommendation: str
    human_review_required: bool
    status: str = "open"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    evidence_links: list[FindingEvidenceLink] = Field(default_factory=list)
