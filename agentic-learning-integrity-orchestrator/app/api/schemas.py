from __future__ import annotations

from pydantic import BaseModel


class ObjectivePayload(BaseModel):
    id: str
    course_id: str
    title: str
    description: str
    rubric_criteria: list[str]
    expected_evidence_patterns: list[str]
    difficulty_level: str


class SupportPayload(BaseModel):
    student_id: str
    objective: ObjectivePayload
    source_type: str
    activity_type: str
    submission_id: str
    artifact_ref: str
    content: str
    draft_count: int = 1
    time_spent_estimate: float = 1.0
