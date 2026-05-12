CREATE TABLE IF NOT EXISTS action_mandates (
    mandate_id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    target_resource TEXT NOT NULL,
    decision TEXT NOT NULL,
    audit_reference TEXT NOT NULL,
    typed_intent_json TEXT NOT NULL,
    constraints_applied_json TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS validation_traces (
    trace_id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL,
    policy_ids_json TEXT NOT NULL,
    state_assertions_used_json TEXT NOT NULL,
    decision_path_json TEXT NOT NULL,
    evaluated_predicates_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    audit_event_id TEXT PRIMARY KEY,
    reference TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_reference ON audit_events(reference);

CREATE TABLE IF NOT EXISTS idempotency_keys (
    idempotency_key TEXT PRIMARY KEY,
    mandate_id TEXT NOT NULL,
    response_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
