from __future__ import annotations

from datetime import datetime, UTC

from pydantic import BaseModel, Field


class EvidenceArtifact(BaseModel):
    id: str
    evidence_id: str
    file_name: str
    storage_path: str
    mime_type: str
    size_bytes: int
    sha256: str
    preview_text: str | None = None


class Evidence(BaseModel):
    id: str
    scope_id: str
    title: str
    description: str = ""
    source_type: str
    source_name: str
    source_author: str | None = None
    evidence_type: str
    mime_type: str
    captured_at: datetime | None = None
    uploaded_by: str
    storage_path: str
    content_hash: str
    normalized_text: str = ""
    metadata_json: dict = Field(default_factory=dict)
    classification: str = "unknown"
    sufficiency_status: str = "unknown"
    freshness_status: str = "unknown"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    artifacts: list[EvidenceArtifact] = Field(default_factory=list)
