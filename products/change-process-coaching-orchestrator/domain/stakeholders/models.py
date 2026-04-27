from __future__ import annotations

from pydantic import BaseModel


class StakeholderEntry(BaseModel):
    actor: str
    role: str = "stakeholder"
    influence: str
    alignment: str
    resistance_level: str = "unknown"
    readiness_level: str = "unknown"
    support_needed: str
    notes: str = ""
