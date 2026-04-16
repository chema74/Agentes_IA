from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel

from agents.friction_analyzer import analyze_friction
from agents.intervention_planner import build_intervention_plan
from agents.signal_recorder import capture_signals
from agents.stakeholder_mapper import map_stakeholders
from agents.supervision_governor import supervision_decision
from core.audit.events import make_audit_event
from core.safety.change_breaker import evaluate_change_breaker
from domain.cases.models import ChangeCase, Recommendation
from services.langsmith.trace_refs import build_audit_reference
from services.storage.repositories import STORE


class OrchestratorInput(BaseModel):
    process_notes: str
    context_type: str = "organizational"
    case_id: str | None = None


class OrchestratorOutput(BaseModel):
    estado_del_proceso_de_cambio: str
    resumen_de_senales_detectadas: list[dict]
    mapa_de_stakeholders_o_contexto_personal: list[dict]
    perfil_de_resistencia: dict
    bloqueos_de_adopcion_detectados: list[dict]
    nivel_de_friccion: dict
    plan_de_intervencion: dict
    hitos_de_transformacion: list[dict]
    alerta_de_fatiga_de_cambio: dict
    revision_humana_requerida: bool
    estado_de_la_puerta_de_supervision_humana: dict
    recomendacion_final: dict
    referencia_de_auditoría: str
    case_id: str


class ChangeProcessCoachingOrchestrator:
    def evaluate(self, payload: OrchestratorInput) -> OrchestratorOutput:
        return self._run(payload, persist_plan=False)

    def intervene(self, payload: OrchestratorInput) -> OrchestratorOutput:
        return self._run(payload, persist_plan=True)

    def _run(self, payload: OrchestratorInput, persist_plan: bool) -> OrchestratorOutput:
        case_id = payload.case_id or f"case-{uuid4().hex[:10]}"
        signals = capture_signals(payload.process_notes)
        resistance, blockers, friction, fatigue = analyze_friction(signals)
        stakeholders = map_stakeholders(payload.context_type)
        plan = build_intervention_plan(friction, resistance, blockers)
        breaker = evaluate_change_breaker(friction, resistance, blockers, fatigue)
        gate, milestones, recommendation = supervision_decision(friction, resistance, breaker.level)
        audit_reference = build_audit_reference(breaker.level, recommendation["summary"])
        change_case = ChangeCase(
            case_id=case_id,
            estado_del_proceso_de_cambio=breaker.status,
            resumen_de_senales_detectadas=signals,
            mapa_de_stakeholders_o_contexto_personal=stakeholders,
            perfil_de_resistencia=resistance,
            bloqueos_de_adopcion_detectados=blockers,
            nivel_de_friccion=friction,
            plan_de_intervencion=plan,
            hitos_de_transformacion=milestones,
            alerta_de_fatiga_de_cambio=fatigue,
            revision_humana_requerida=breaker.human_review_required,
            estado_de_la_puerta_de_supervision_humana=gate,
            recomendacion_final=Recommendation(**recommendation),
            referencia_de_auditoria=audit_reference,
        )
        if persist_plan:
            STORE.save_case(change_case)
        self._append_event(audit_reference, "CHANGE_CASE", case_id, "evaluated", {"status": breaker.status, "level": breaker.level, "persisted": persist_plan})
        return OrchestratorOutput(
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
            referencia_de_auditoría=change_case.referencia_de_auditoria,
            case_id=change_case.case_id,
        )

    def _append_event(self, reference: str, entity_type: str, entity_id: str, action: str, payload: dict) -> None:
        STORE.append_audit_event(make_audit_event(reference, entity_type, entity_id, action, payload))


ORCHESTRATOR = ChangeProcessCoachingOrchestrator()
