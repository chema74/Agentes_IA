from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class NarrativeEpisode(BaseModel):
    episode_id: str
    user_id: str
    user_message: str
    summary: str
    continuity_notes: str
    validated_signals: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
