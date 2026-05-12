from __future__ import annotations

from pydantic import BaseModel


class FeedbackPlan(BaseModel):
    id: str
    evaluation_event_id: str
    feedback_summary: str
    intervention_type: str
    recommended_actions: list[str]
    teacher_notes_required: bool
    followup_window: str
