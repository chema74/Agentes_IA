from __future__ import annotations

from pydantic import BaseModel, Field


class EvidenceRef(BaseModel):
    source_id: str
    source_label: str
    chunk_id: str
    source_excerpt: str
    confidence: float = 0.5


class Clause(BaseModel):
    clause_id: str
    title: str
    clause_type: str
    text: str
    confidence: float = 0.5
    evidence: list[EvidenceRef] = Field(default_factory=list)

