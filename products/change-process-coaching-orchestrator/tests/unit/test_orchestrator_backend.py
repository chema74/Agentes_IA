from __future__ import annotations

from services.orchestration.change_orchestrator import ChangeProcessCoachingOrchestrator, OrchestratorInput


def test_orchestrator_uses_graph_backend_when_available(monkeypatch):
    orchestrator = ChangeProcessCoachingOrchestrator()

    class _StubResult:
        estado_del_proceso_de_cambio = "observation"
        resumen_de_senales_detectadas = []
        mapa_de_stakeholders_o_contexto_personal = []
        perfil_de_resistencia = {}
        bloqueos_de_adopcion_detectados = []
        nivel_de_friccion = {}
        plan_de_intervencion = {}
        hitos_de_transformacion = []
        alerta_de_fatiga_de_cambio = {}
        revision_humana_requerida = False
        estado_de_la_puerta_de_supervision_humana = {}
        recomendacion_final = {}
        referencia_de_auditoria = "audit-graph"
        case_id = "case-graph"

    expected = _StubResult()

    def _fake_graph(payload, persist_plan=False):
        return expected

    monkeypatch.setattr(orchestrator, "_run_via_graph", _fake_graph)
    result = orchestrator.evaluate(OrchestratorInput(process_notes="test"))
    assert result is expected


def test_orchestrator_falls_back_to_local_backend(monkeypatch):
    orchestrator = ChangeProcessCoachingOrchestrator()
    monkeypatch.setattr(orchestrator, "_run_via_graph", lambda payload, persist_plan=False: None)
    result = orchestrator.evaluate(OrchestratorInput(process_notes="Hay ambiguedad y fatiga."))
    assert result.case_id
    assert result.estado_del_proceso_de_cambio
