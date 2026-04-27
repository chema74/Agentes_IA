from __future__ import annotations

from pydantic import BaseModel, Field

from domain.cases.models import ChangeSessionNote, ChangeTaskRecord, IntakeSourceRef, SurveySignalInput
from domain.signals.models import ChangeSignal
from domain.stakeholders.models import StakeholderEntry


class ChangeCasePayload(BaseModel):
    process_notes: str
    context_type: str = "organizational"
    change_goal: str = ""
    change_phase: str = "assessment"
    requested_mode: str = "evaluate"
    case_id: str | None = None
    signals: list[ChangeSignal] = Field(default_factory=list)
    stakeholders: list[StakeholderEntry] = Field(default_factory=list)
    sessions: list[ChangeSessionNote] = Field(default_factory=list)
    tasks: list[ChangeTaskRecord] = Field(default_factory=list)
    survey_inputs: list[SurveySignalInput] = Field(default_factory=list)
    source_systems: list[IntakeSourceRef] = Field(default_factory=list)
