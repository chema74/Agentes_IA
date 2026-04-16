from __future__ import annotations

from uuid import uuid4

from domain.cases.models import ChangeSessionNote, ChangeTaskRecord, SurveySignalInput
from domain.signals.models import ChangeSignal
from services.llm.groq_client import GROQ_CLIENT


def _notes_to_sentences(process_notes: str, sessions: list[ChangeSessionNote]) -> list[str]:
    items = [part.strip() for part in process_notes.split(".") if part.strip()]
    items.extend(note.summary.strip() for note in sessions if note.summary.strip())
    return items


def _task_to_signal(task: ChangeTaskRecord) -> ChangeSignal | None:
    status = task.status.lower()
    if status in {"blocked", "at_risk", "delayed"}:
        return ChangeSignal(
            signal_id=f"signal-{uuid4().hex[:10]}",
            category="execution_block",
            summary=f"Tarea en riesgo: {task.title}",
            intensity="high" if status == "blocked" else "medium",
            source="task_tracker",
            evidence_excerpt=f"owner={task.owner}; due_window={task.due_window}; status={task.status}",
            confidence=0.82,
        )
    if status in {"done", "completed"}:
        return ChangeSignal(
            signal_id=f"signal-{uuid4().hex[:10]}",
            category="progress",
            summary=f"Hito completado: {task.title}",
            intensity="low",
            source="task_tracker",
            evidence_excerpt=f"owner={task.owner}; status={task.status}",
            confidence=0.75,
        )
    return None


def _survey_to_signal(survey_input: SurveySignalInput) -> ChangeSignal:
    category, intensity = GROQ_CLIENT.classify_signal(f"{survey_input.prompt}. {survey_input.response}")
    return ChangeSignal(
        signal_id=f"signal-{uuid4().hex[:10]}",
        category=category,
        summary=f"{survey_input.prompt}: {survey_input.response}",
        intensity=intensity,
        source="survey",
        evidence_excerpt=f"score={survey_input.score}" if survey_input.score is not None else survey_input.response,
        confidence=0.68,
    )


def capture_signals(
    process_notes: str,
    sessions: list[ChangeSessionNote] | None = None,
    tasks: list[ChangeTaskRecord] | None = None,
    survey_inputs: list[SurveySignalInput] | None = None,
    explicit_signals: list[ChangeSignal] | None = None,
) -> list[ChangeSignal]:
    items: list[ChangeSignal] = list(explicit_signals or [])
    sessions = sessions or []
    tasks = tasks or []
    survey_inputs = survey_inputs or []
    for sentence in _notes_to_sentences(process_notes, sessions):
        category, intensity = GROQ_CLIENT.classify_signal(sentence)
        items.append(
            ChangeSignal(
                signal_id=f"signal-{uuid4().hex[:10]}",
                category=category,
                summary=sentence,
                intensity=intensity,
                source="direct_input",
                evidence_excerpt=sentence,
                confidence=0.72,
            )
        )
    for task in tasks:
        task_signal = _task_to_signal(task)
        if task_signal is not None:
            items.append(task_signal)
    for survey_input in survey_inputs:
        items.append(_survey_to_signal(survey_input))
    return items
