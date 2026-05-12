from __future__ import annotations

from services.orchestration.psychological_orchestrator import ORCHESTRATOR, OrchestratorInput
from services.storage.repositories import STORE


def test_orchestrator_returns_required_contract_fields():
    result = ORCHESTRATOR.invoke(OrchestratorInput(user_id="user-a", message="Estoy triste y muy solo hoy."))
    payload = result.model_dump(mode="json")
    for key in [
        "affective_state",
        "inferred_risk_level",
        "continuity_notes",
        "validated_signals",
        "intervention_style",
        "recommended_next_step",
        "escalation_status",
        "safety_notes",
        "narrative_memory_reference",
    ]:
        assert key in payload


def test_orchestrator_persists_episode_and_neuro_state():
    user_id = "user-b"
    ORCHESTRATOR.invoke(OrchestratorInput(user_id=user_id, message="Tengo ansiedad y me siento bloqueado."))
    assert STORE.get_neuro_state(user_id) is not None
    assert STORE.get_recent_episodes(user_id)
