CREATE TABLE IF NOT EXISTS neuro_states (
    user_id TEXT PRIMARY KEY,
    serotonin REAL NOT NULL,
    dopamine REAL NOT NULL,
    cortisol REAL NOT NULL,
    oxytocin REAL NOT NULL,
    arousal REAL NOT NULL,
    valence REAL NOT NULL,
    emotional_stability REAL NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS archetype_profiles (
    user_id TEXT NOT NULL,
    dominant_archetype TEXT NOT NULL,
    narrative_pattern TEXT NOT NULL,
    symbolic_notes TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS narrative_episodes (
    episode_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    summary TEXT NOT NULL,
    continuity_notes TEXT NOT NULL,
    validated_signals TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cbt_interventions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    intervention_style TEXT NOT NULL,
    rationale TEXT NOT NULL,
    prompt_frame TEXT NOT NULL,
    recommended_next_step TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_events (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    inferred_risk_level TEXT NOT NULL,
    escalation_status TEXT NOT NULL,
    matched_signals TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
