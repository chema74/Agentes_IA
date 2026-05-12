from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class NeuroState(BaseModel):
    user_id: str
    serotonin: float = 0.5
    dopamine: float = 0.5
    cortisol: float = 0.5
    oxytocin: float = 0.5
    arousal: float = 0.5
    valence: float = 0.5
    emotional_stability: float = 0.5
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AffectiveState(BaseModel):
    primary_emotion: str
    secondary_emotion: str | None = None
    intensity: float
    affective_summary: str
