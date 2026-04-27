CREATE TABLE IF NOT EXISTS trade_cases (
    case_id TEXT PRIMARY KEY,
    signal_status TEXT NOT NULL,
    international_risk_level TEXT NOT NULL,
    human_review_required INTEGER NOT NULL,
    review_gate_status TEXT NOT NULL,
    audit_reference TEXT NOT NULL,
    payload_json TEXT NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_trade_audit_reference ON audit_events(reference);
