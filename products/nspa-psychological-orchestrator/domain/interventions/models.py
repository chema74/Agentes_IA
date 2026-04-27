from __future__ import annotations

from pydantic import BaseModel


class CBTIntervention(BaseModel):
    intervention_style: str
    rationale: str
    prompt_frame: str
    recommended_next_step: str
