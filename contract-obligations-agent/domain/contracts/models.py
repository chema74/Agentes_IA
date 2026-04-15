from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from domain.clauses.models import Clause, EvidenceRef
from domain.obligations.models import Obligation
from domain.risk_flags.models import Alert, RiskAssessment

class DocumentType(str, Enum):
    contract = "contract"
    annex = "annex"
    email = "email"
    template = "template"
    unknown = "unknown"


class TextChunk(BaseModel):
    chunk_id: str
    text: str
    source_label: str
    start_char: int = 0
    end_char: int = 0


class ParsedDocument(BaseModel):
    document_id: str
    filename: str
    document_type: DocumentType
    metadata: dict = Field(default_factory=dict)
    raw_text: str
    normalized_text: str
    chunks: list[TextChunk] = Field(default_factory=list)


class ContractDocument(BaseModel):
    document_id: str
    filename: str
    document_type: DocumentType
    metadata: dict = Field(default_factory=dict)
    raw_text: str
    normalized_text: str
    chunks: list[TextChunk] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutiveSummary(BaseModel):
    executive_summary: str
    key_points: list[str] = Field(default_factory=list)
    human_review_note: str = ""


class ContractAnalysis(BaseModel):
    document_id: str
    filename: str
    document_type: DocumentType
    metadata: dict = Field(default_factory=dict)
    raw_text: str
    normalized_text: str
    chunks: list[TextChunk] = Field(default_factory=list)
    clauses: list[Clause] = Field(default_factory=list)
    obligations: list[Obligation] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)
    risk_assessment: RiskAssessment | None = None
    summary: ExecutiveSummary = Field(default_factory=lambda: ExecutiveSummary(executive_summary=""))
    comparison: dict = Field(default_factory=dict)
    evidences: list[EvidenceRef] = Field(default_factory=list)
    retrieval_hits: list[dict] = Field(default_factory=list)
