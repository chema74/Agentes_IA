from __future__ import annotations

import pytest

from services.orchestration.change_orchestrator import OrchestratorInput
from services.orchestration.graph_runtime import StateGraph, build_change_process_graph, run_change_process_graph
from services.storage.repositories import STORE


@pytest.mark.skipif(StateGraph is None, reason="LangGraph no instalado en el entorno actual.")
def test_build_change_process_graph_exposes_multi_node_runtime():
    graph = build_change_process_graph()
    assert graph is not None


@pytest.mark.skipif(StateGraph is None, reason="LangGraph no instalado en el entorno actual.")
def test_graph_runtime_returns_orchestrator_compatible_contract():
    result = run_change_process_graph(
        OrchestratorInput(
            process_notes="Hay ambiguedad sobre prioridades. Existe fatiga alta y retrasos sostenidos.",
            context_type="organizational",
            change_goal="Reorganizar la adopcion del cambio",
        )
    )
    payload = result.model_dump(mode="json", by_alias=True)
    for key in [
        "estado_del_proceso_de_cambio",
        "resumen_de_senales_detectadas",
        "mapa_de_stakeholders_o_contexto_personal",
        "perfil_de_resistencia",
        "bloqueos_de_adopcion_detectados",
        "nivel_de_friccion",
        "plan_de_intervencion",
        "hitos_de_transformacion",
        "alerta_de_fatiga_de_cambio",
        "revision_humana_requerida",
        "estado_de_la_puerta_de_supervision_humana",
        "recomendacion_final",
        "referencia_de_auditor\u00eda",
        "case_id",
    ]:
        assert key in payload


@pytest.mark.skipif(StateGraph is None, reason="LangGraph no instalado en el entorno actual.")
def test_graph_runtime_can_persist_case():
    result = run_change_process_graph(
        OrchestratorInput(
            process_notes="Existe conflicto interpersonal y bloqueo operativo.",
            context_type="organizational",
        ),
        persist_plan=True,
    )
    saved = STORE.get_case(result.case_id)
    assert saved is not None
    assert saved.case_id == result.case_id
