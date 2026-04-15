from __future__ import annotations

from services.orchestration.psychological_orchestrator import ORCHESTRATOR, OrchestratorInput


def test_continuity_notes_reference_previous_episode():
    user_id = "user-cont"
    ORCHESTRATOR.invoke(OrchestratorInput(user_id=user_id, message="Me siento cansado desde hace dias."))
    second = ORCHESTRATOR.invoke(OrchestratorInput(user_id=user_id, message="Hoy sigo igual y me noto mas ansioso."))
    assert "Ultimo episodio recordado" in second.continuity_notes
    assert second.narrative_memory_reference
