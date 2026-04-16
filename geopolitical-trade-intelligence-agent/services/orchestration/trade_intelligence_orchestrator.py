from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel

from agents.exposure_analyzer import analyze_exposure
from agents.geopolitical_signal_recorder import record_signals
from agents.international_decision_governor import decide_operational_recommendation
from agents.route_risk_mapper import map_route_risk
from agents.trade_policy_interpreter import interpret_trade_policy
from core.audit.events import make_audit_event
from core.safety.trade_breaker import evaluate_trade_breaker
from domain.cases.models import TradeCase
from services.langsmith.trace_refs import build_audit_reference
from services.storage.repositories import STORE


class OrchestratorInput(BaseModel):
    signal_text: str
    country: str
    sector: str
    product: str | None = None
    route: str | None = None
    case_id: str | None = None


class OrchestratorOutput(BaseModel):
    estado_de_la_señal_geopolítica: str
    resumen_del_perfil_de_riesgo_país: dict
    mapa_de_exposición_comercial: dict
    eventos_de_sanción_o_restricción_detectados: list[dict]
    alertas_de_disrupción_de_ruta: list[dict]
    nivel_de_riesgo_internacional: str
    escenarios_relevantes: list[str]
    recomendación_operativa: str
    revisión_humana_requerida: bool
    estado_de_la_puerta_de_revisión_humana: dict
    memorando_de_decisión_exportadora: dict
    referencia_de_auditoría: str
    case_id: str


class GeopoliticalTradeIntelligenceOrchestrator:
    def evaluate(self, payload: OrchestratorInput) -> OrchestratorOutput:
        return self._run(payload, persist_case=True)

    def assess_route(self, payload: OrchestratorInput) -> OrchestratorOutput:
        return self._run(payload, persist_case=True)

    def _run(self, payload: OrchestratorInput, persist_case: bool) -> OrchestratorOutput:
        case_id = payload.case_id or f"case-{uuid4().hex[:10]}"
        signals = record_signals(payload.signal_text, payload.country)
        sanction_events = interpret_trade_policy(signals)
        country_profile, exposure = analyze_exposure(payload.country, payload.sector, payload.product, payload.route, signals)
        route_alerts = map_route_risk(payload.route, signals)
        confidence = 0.9 if not sanction_events and not route_alerts else 0.7 if route_alerts or sanction_events else 0.85
        breaker = evaluate_trade_breaker(sanction_events, route_alerts, confidence, country_profile.geopolitical_risk)
        recommendation, gate, memorandum, scenarios = decide_operational_recommendation(breaker.level, payload.country, confidence)
        audit_reference = build_audit_reference(breaker.level, payload.country)
        trade_case = TradeCase(
            case_id=case_id,
            estado_de_la_señal_geopolítica=breaker.status,
            resumen_del_perfil_de_riesgo_país=country_profile,
            mapa_de_exposición_comercial=exposure,
            eventos_de_sanción_o_restricción_detectados=sanction_events,
            alertas_de_disrupción_de_ruta=route_alerts,
            nivel_de_riesgo_internacional=f"Nivel {breaker.level}",
            escenarios_relevantes=scenarios,
            recomendación_operativa=recommendation,
            revisión_humana_requerida=breaker.human_review_required,
            estado_de_la_puerta_de_revisión_humana=gate,
            memorando_de_decisión_exportadora=memorandum,
            referencia_de_auditoría=audit_reference,
            señales=signals,
        )
        if persist_case:
            STORE.save_case(trade_case)
        self._append_event(audit_reference, "TRADE_CASE", case_id, "evaluated", {"country": payload.country, "level": breaker.level})
        return OrchestratorOutput(
            estado_de_la_señal_geopolítica=trade_case.estado_de_la_señal_geopolítica,
            resumen_del_perfil_de_riesgo_país=trade_case.resumen_del_perfil_de_riesgo_país.model_dump(mode="json"),
            mapa_de_exposición_comercial=trade_case.mapa_de_exposición_comercial.model_dump(mode="json"),
            eventos_de_sanción_o_restricción_detectados=[item.model_dump(mode="json") for item in trade_case.eventos_de_sanción_o_restricción_detectados],
            alertas_de_disrupción_de_ruta=[item.model_dump(mode="json") for item in trade_case.alertas_de_disrupción_de_ruta],
            nivel_de_riesgo_internacional=trade_case.nivel_de_riesgo_internacional,
            escenarios_relevantes=trade_case.escenarios_relevantes,
            recomendación_operativa=trade_case.recomendación_operativa,
            revisión_humana_requerida=trade_case.revisión_humana_requerida,
            estado_de_la_puerta_de_revisión_humana=trade_case.estado_de_la_puerta_de_revisión_humana.model_dump(mode="json"),
            memorando_de_decisión_exportadora=trade_case.memorando_de_decisión_exportadora.model_dump(mode="json"),
            referencia_de_auditoría=trade_case.referencia_de_auditoría,
            case_id=trade_case.case_id,
        )

    def _append_event(self, reference: str, entity_type: str, entity_id: str, action: str, payload: dict) -> None:
        STORE.append_audit_event(make_audit_event(reference, entity_type, entity_id, action, payload))


ORCHESTRATOR = GeopoliticalTradeIntelligenceOrchestrator()
