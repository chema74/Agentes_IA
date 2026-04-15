from __future__ import annotations

from services.orchestration.psychological_orchestrator import ORCHESTRATOR, OrchestratorInput


if __name__ == "__main__":
    sample = OrchestratorInput(user_id="demo-user", message="Estoy agotado y me siento solo desde hace dias.")
    result = ORCHESTRATOR.invoke(sample)
    print(result.model_dump_json(indent=2))
