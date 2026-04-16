from __future__ import annotations

from typing import Any, TypedDict
from uuid import uuid4

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    END = "END"
    START = "START"
    StateGraph = None

from agents.friction_analyzer import analyze_friction
from agents.intervention_planner import build_intervention_plan
from agents.signal_recorder import capture_signals
from agents.stakeholder_mapper import map_stakeholders
from agents.supervision_governor import supervision_decision
from core.audit.events import make_audit_event
from core.safety.change_breaker import evaluate_change_breaker
from domain.cases.models import ChangeCase, Recommendation
from services.langsmith.trace_refs import build_audit_reference
from services.orchestration.change_orchestrator import OrchestratorInput, OrchestratorOutput
from services.storage.repositories import STORE


class ChangeGraphState(TypedDict, total=False):
    process_notes: str
    context_type: str
    change_goal: str
    change_phase: str
    requested_mode: str
    case_id: str | None
    persist_plan: bool
    signals: list[Any]
    stakeholders: list[Any]
    sessions: list[Any]
    tasks: list[Any]
    survey_inputs: list[Any]
    source_systems: list[Any]
    resistance: Any
    blockers: list[Any]
    friction: Any
    fatigue: Any
    plan: Any
    breaker: Any
    supervision_gate: Any
    milestones: list[Any]
    recommendation: dict[str, Any]
    audit_reference: str
    change_case: ChangeCase
    orchestrator_output: OrchestratorOutput
    result: dict[str, Any]


def _input_to_state(payload: OrchestratorInput, persist_plan: bool) -> ChangeGraphState:
    return {
        "process_notes": payload.process_notes,
        "context_type": payload.context_type,
        "change_goal": payload.change_goal,
        "change_phase": payload.change_phase,
        "requested_mode": payload.requested_mode,
        "case_id": payload.case_id,
        "persist_plan": persist_plan,
        "signals": payload.signals,
        "stakeholders": payload.stakeholders,
        "sessions": payload.sessions,
        "tasks": payload.tasks,
        "survey_inputs": payload.survey_inputs,
        "source_systems": payload.source_systems,
    }


def signal_recorder_node(state: ChangeGraphState) -> ChangeGraphState:
    case_id = state.get("case_id") or f"case-{uuid4().hex[:10]}"
    signals = capture_signals(
        state["process_notes"],
        sessions=state.get("sessions"),
        tasks=state.get("tasks"),
        survey_inputs=state.get("survey_inputs"),
        explicit_signals=state.get("signals"),
    )
    return {"case_id": case_id, "signals": signals}


def friction_analyzer_node(state: ChangeGraphState) -> ChangeGraphState:
    resistance, blockers, friction, fatigue = analyze_friction(state["signals"])
    return {
        "resistance": resistance,
        "blockers": blockers,
        "friction": friction,
        "fatigue": fatigue,
    }


def stakeholder_mapper_node(state: ChangeGraphState) -> ChangeGraphState:
    stakeholders = map_stakeholders(state.get("context_type", "organizational"), state.get("stakeholders"))
    return {"stakeholders": stakeholders}


def intervention_planner_node(state: ChangeGraphState) -> ChangeGraphState:
    plan = build_intervention_plan(state["friction"], state["resistance"], state["blockers"])
    return {"plan": plan}


def supervision_governor_node(state: ChangeGraphState) -> ChangeGraphState:
    breaker = evaluate_change_breaker(state["friction"], state["resistance"], state["blockers"], state["fatigue"])
    gate, milestones, recommendation = supervision_decision(state["friction"], state["resistance"], breaker.level)
    audit_reference = build_audit_reference(breaker.level, recommendation["summary"])
    return {
        "breaker": breaker,
        "supervision_gate": gate,
        "milestones": milestones,
        "recommendation": recommendation,
        "audit_reference": audit_reference,
    }


def finalizer_node(state: ChangeGraphState) -> ChangeGraphState:
    change_case = ChangeCase(
        case_id=state["case_id"],
        estado_del_proceso_de_cambio=state["breaker"].status,
        resumen_de_senales_detectadas=state["signals"],
        mapa_de_stakeholders_o_contexto_personal=state["stakeholders"],
        perfil_de_resistencia=state["resistance"],
        bloqueos_de_adopcion_detectados=state["blockers"],
        nivel_de_friccion=state["friction"],
        plan_de_intervencion=state["plan"],
        hitos_de_transformacion=state["milestones"],
        alerta_de_fatiga_de_cambio=state["fatigue"],
        revision_humana_requerida=state["breaker"].human_review_required,
        estado_de_la_puerta_de_supervision_humana=state["supervision_gate"],
        recomendacion_final=Recommendation(**state["recommendation"]),
        referencia_de_auditoria=state["audit_reference"],
    )
    if state.get("persist_plan"):
        STORE.save_case(change_case)
    STORE.append_audit_event(
        make_audit_event(
            state["audit_reference"],
            "CHANGE_CASE",
            state["case_id"],
            "evaluated",
            {
                "status": state["breaker"].status,
                "level": state["breaker"].level,
                "persisted": state.get("persist_plan", False),
                "change_goal": state.get("change_goal", ""),
                "change_phase": state.get("change_phase", ""),
                "requested_mode": state.get("requested_mode", ""),
                "breaker_reason_codes": state["breaker"].reason_codes,
                "breaker_evidence": state["breaker"].evidence_bundle,
            },
        )
    )
    result = OrchestratorOutput(
        estado_del_proceso_de_cambio=change_case.estado_del_proceso_de_cambio,
        resumen_de_senales_detectadas=[item.model_dump(mode="json") for item in change_case.resumen_de_senales_detectadas],
        mapa_de_stakeholders_o_contexto_personal=[item.model_dump(mode="json") for item in change_case.mapa_de_stakeholders_o_contexto_personal],
        perfil_de_resistencia=change_case.perfil_de_resistencia.model_dump(mode="json"),
        bloqueos_de_adopcion_detectados=[item.model_dump(mode="json") for item in change_case.bloqueos_de_adopcion_detectados],
        nivel_de_friccion=change_case.nivel_de_friccion.model_dump(mode="json"),
        plan_de_intervencion=change_case.plan_de_intervencion.model_dump(mode="json"),
        hitos_de_transformacion=[item.model_dump(mode="json") for item in change_case.hitos_de_transformacion],
        alerta_de_fatiga_de_cambio=change_case.alerta_de_fatiga_de_cambio.model_dump(mode="json"),
        revision_humana_requerida=change_case.revision_humana_requerida,
        estado_de_la_puerta_de_supervision_humana=change_case.estado_de_la_puerta_de_supervision_humana.model_dump(mode="json"),
        recomendacion_final=change_case.recomendacion_final.model_dump(mode="json"),
        referencia_de_auditoria=change_case.referencia_de_auditoria,
        case_id=change_case.case_id,
    )
    return {
        "change_case": change_case,
        "orchestrator_output": result,
        "result": result.model_dump(mode="json", by_alias=True),
    }


def build_change_process_graph():
    if StateGraph is None:
        return None

    graph = StateGraph(ChangeGraphState)
    graph.add_node("signal_recorder", signal_recorder_node)
    graph.add_node("friction_analyzer", friction_analyzer_node)
    graph.add_node("stakeholder_mapper", stakeholder_mapper_node)
    graph.add_node("intervention_planner", intervention_planner_node)
    graph.add_node("supervision_governor", supervision_governor_node)
    graph.add_node("finalizer", finalizer_node)
    graph.add_edge(START, "signal_recorder")
    graph.add_edge("signal_recorder", "friction_analyzer")
    graph.add_edge("friction_analyzer", "stakeholder_mapper")
    graph.add_edge("stakeholder_mapper", "intervention_planner")
    graph.add_edge("intervention_planner", "supervision_governor")
    graph.add_edge("supervision_governor", "finalizer")
    graph.add_edge("finalizer", END)
    return graph.compile()


def run_change_process_graph(payload: OrchestratorInput, persist_plan: bool = False) -> OrchestratorOutput:
    graph = build_change_process_graph()
    if graph is None:
        raise RuntimeError("LangGraph is not available in the current environment.")
    result_state = graph.invoke(_input_to_state(payload, persist_plan))
    return result_state["orchestrator_output"]
