from __future__ import annotations

from pydantic import BaseModel


class ResistanceProfile(BaseModel):
    resistance_type: str
    intensity: str
    rationale: str
