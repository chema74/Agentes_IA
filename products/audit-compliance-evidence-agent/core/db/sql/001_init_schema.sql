CREATE TABLE IF NOT EXISTS audit_scopes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    framework TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    period_start DATE NULL,
    period_end DATE NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS controls (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL REFERENCES audit_scopes(id),
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    criticality TEXT NOT NULL,
    expected_criterion TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    owner_user_id TEXT NULL,
    version TEXT NOT NULL DEFAULT '1.0',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL REFERENCES audit_scopes(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_author TEXT NULL,
    evidence_type TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    captured_at TIMESTAMP NULL,
    uploaded_by TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    normalized_text TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    classification TEXT NOT NULL DEFAULT 'unknown',
    sufficiency_status TEXT NOT NULL DEFAULT 'unknown',
    freshness_status TEXT NOT NULL DEFAULT 'unknown',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence_artifacts (
    id TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    file_name TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    preview_text TEXT NULL
);

CREATE TABLE IF NOT EXISTS control_evidence_mappings (
    id TEXT PRIMARY KEY,
    control_id TEXT NOT NULL REFERENCES controls(id),
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    mapping_mode TEXT NOT NULL,
    confidence REAL NOT NULL,
    rationale TEXT NOT NULL,
    support_excerpt TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'pending_review',
    reviewed_by TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coverage_evaluations (
    id TEXT PRIMARY KEY,
    control_id TEXT NOT NULL REFERENCES controls(id),
    scope_id TEXT NOT NULL REFERENCES audit_scopes(id),
    coverage_status TEXT NOT NULL,
    coverage_score REAL NOT NULL,
    explanation TEXT NOT NULL,
    evaluated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    evaluated_by_system BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS gaps (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL REFERENCES audit_scopes(id),
    control_id TEXT NOT NULL REFERENCES controls(id),
    gap_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    explanation TEXT NOT NULL,
    human_review_required BOOLEAN NOT NULL DEFAULT TRUE,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL REFERENCES audit_scopes(id),
    control_id TEXT NOT NULL REFERENCES controls(id),
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    explanation TEXT NOT NULL,
    confidence REAL NOT NULL,
    preliminary_recommendation TEXT NOT NULL,
    human_review_required BOOLEAN NOT NULL DEFAULT TRUE,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finding_evidence_links (
    id TEXT PRIMARY KEY,
    finding_id TEXT NOT NULL REFERENCES findings(id),
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    relationship_type TEXT NOT NULL,
    commentary TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS remediations (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL REFERENCES audit_scopes(id),
    finding_id TEXT NOT NULL REFERENCES findings(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed',
    owner_user_id TEXT NULL,
    target_date DATE NULL,
    completion_note TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_packages (
    id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL REFERENCES audit_scopes(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    summary_json TEXT NOT NULL DEFAULT '{}',
    storage_path TEXT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    scope_id TEXT NULL REFERENCES audit_scopes(id),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_user_id TEXT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_role_assignments (
    id TEXT PRIMARY KEY,
    scope_id TEXT NULL REFERENCES audit_scopes(id),
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
