from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field

from domain.clauses.models import EvidenceRef


class ObligationStatus(str, Enum):
    open = "open"
    done = "done"
    pending_review = "pending_review"


class Obligation(BaseModel):
    obligation_id: str
    description: str
    responsible_party: str | None = None
    due_date: str | None = None
    dependency: str | None = None
    observations: str | None = None
    confidence: float = 0.5
    status: ObligationStatus = ObligationStatus.open
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ObligationMatrix(BaseModel):
    obligations: list[Obligation] = Field(default_factory=list)

