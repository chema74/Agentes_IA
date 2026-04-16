CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    action_types TEXT NOT NULL,
    predicates TEXT NOT NULL,
    decision_on_failure TEXT NOT NULL,
    priority INTEGER NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS symbolic_states (
    entity_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    assertions TEXT NOT NULL,
    inconsistencies_detected TEXT NOT NULL,
    last_validated_at TEXT NOT NULL,
    PRIMARY KEY (entity_id, entity_type)
);
