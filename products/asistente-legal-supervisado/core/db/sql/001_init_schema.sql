CREATE TABLE IF NOT EXISTS contract_reviews (
    review_id TEXT PRIMARY KEY,
    contract_type TEXT NOT NULL,
    approval_recommendation TEXT NOT NULL,
    human_review_required INTEGER NOT NULL,
    negotiation_status TEXT NOT NULL,
    audit_reference TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS negotiation_tracks (
    track_id TEXT PRIMARY KEY,
    review_id TEXT NOT NULL,
    issue_key TEXT NOT NULL,
    round_number INTEGER NOT NULL,
    status TEXT NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_legal_audit_reference ON audit_events(reference);
