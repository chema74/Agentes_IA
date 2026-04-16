from __future__ import annotations

from pydantic import BaseModel, Field


class ResistanceProfile(BaseModel):
    resistance_type: str
    intensity: str
    rationale: str
    legitimacy: str = "mixed"
    manifestations: list[str] = Field(default_factory=list)
    inferred_from_signal_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.7
