from __future__ import annotations

from pydantic import BaseModel


class StakeholderEntry(BaseModel):
    actor: str
    influence: str
    alignment: str
    support_needed: str
