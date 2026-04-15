from __future__ import annotations

CREATE TABLE IF NOT EXISTS learning_objectives (
    id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    rubric_criteria TEXT NOT NULL,
    expected_evidence_patterns TEXT NOT NULL,
    difficulty_level TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence_traces (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    objective_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    artifact_ref TEXT NOT NULL,
    draft_count INTEGER NOT NULL,
    revision_markers TEXT NOT NULL,
    time_spent_estimate REAL NOT NULL,
    quality_markers TEXT NOT NULL,
    stability_markers TEXT NOT NULL,
    process_summary TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluation_events (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    objective_id TEXT NOT NULL,
    submission_id TEXT NOT NULL,
    rubric_snapshot TEXT NOT NULL,
    evidence_refs TEXT NOT NULL,
    performance_summary TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    evaluation_state TEXT NOT NULL,
    teacher_review_required BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS integrity_alerts (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    evaluation_event_id TEXT NOT NULL,
    signal_level INTEGER NOT NULL,
    signal_type TEXT NOT NULL,
    description TEXT NOT NULL,
    supporting_evidence_refs TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    circuit_breaker_triggered BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
