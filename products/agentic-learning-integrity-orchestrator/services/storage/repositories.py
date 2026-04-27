from __future__ import annotations

from dataclasses import dataclass, field

from domain.evidence.models import EvidenceTrace
from domain.evaluation.models import EvaluationEvent
from domain.feedback.models import FeedbackPlan
from domain.integrity.models import IntegrityAlert
from domain.objectives.models import LearningObjective
from domain.overrides.models import TeacherOverride


@dataclass
class IntegrityStore:
    objectives: dict[str, LearningObjective] = field(default_factory=dict)
    traces: dict[str, list[EvidenceTrace]] = field(default_factory=dict)
    evaluations: dict[str, EvaluationEvent] = field(default_factory=dict)
    alerts: dict[str, list[IntegrityAlert]] = field(default_factory=dict)
    feedback_plans: dict[str, FeedbackPlan] = field(default_factory=dict)
    overrides: dict[str, TeacherOverride] = field(default_factory=dict)

    def add_trace(self, student_id: str, trace: EvidenceTrace) -> None:
        self.traces.setdefault(student_id, []).append(trace)

    def get_traces(self, student_id: str) -> list[EvidenceTrace]:
        return self.traces.get(student_id, [])


STORE = IntegrityStore()
