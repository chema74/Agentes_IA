from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class NegotiationTrack(BaseModel):
    track_id: str
    review_id: str
    issue_key: str
    round_number: int
    counterparty_name: str
    our_position: str
    allowed_concession_range: str
    counterparty_response: str | None = None
    status: str
    audit_reference: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
