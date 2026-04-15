from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from agents.affective_signal_interpreter import interpret_affective_signals
from agents.archetypal_mapper import map_archetype
from agents.cbt_intervention_guide import select_cbt_intervention
from agents.narrative_continuity_keeper import continuity_notes_from_history
from agents.neuro_state_modeler import update_neuro_state
from agents.psychological_safety_circuit_breaker import run_circuit_breaker
from core.config.settings import settings
from domain.narrative.models import NarrativeEpisode
from domain.risk.models import RiskEvent
from services.llm.gemini_client import GeminiClient
from services.retrieval.memory_retriever import retrieve_relevant_episodes
from services.storage.repositories import STORE


class OrchestratorInput(BaseModel):
    user_id: str
    message: str


class OrchestratorOutput(BaseModel):
    affective_state: dict
    inferred_risk_level: str
    continuity_notes: str
    validated_signals: list[str]
    intervention_style: str
    recommended_next_step: str
    escalation_status: str
    safety_notes: list[str]
    narrative_memory_reference: list[str] = Field(default_factory=list)
    response_text: str


class PsychologicalOrchestrator:
    def __init__(self) -> None:
        self.llm = GeminiClient(settings.gemini_model)

    def invoke(self, payload: OrchestratorInput) -> OrchestratorOutput:
        history = STORE.get_recent_episodes(payload.user_id, limit=settings.max_memory_results)
        memory_refs = retrieve_relevant_episodes(history, payload.message, limit=3)
        continuity = continuity_notes_from_history(history)

        affective = interpret_affective_signals(payload.message)
        safety = run_circuit_breaker(payload.message)
        archetype = map_archetype(payload.message)
        neuro_state = update_neuro_state(payload.user_id, STORE.get_neuro_state(payload.user_id), affective["validated_signals"])
        STORE.save_neuro_state(neuro_state)

        intervention = select_cbt_intervention(safety.inferred_risk_level, affective["affective_state"].primary_emotion, continuity)
        summary = self.llm.summarize(payload.message)

        response_text = self._compose_response(
            affective_summary=affective["affective_state"].affective_summary,
            safety=safety,
            intervention_style=intervention.intervention_style,
            next_step=intervention.recommended_next_step,
            continuity=continuity,
            archetype=archetype.symbolic_notes,
        )

        episode = NarrativeEpisode(
            episode_id=f"episode-{uuid4().hex[:12]}",
            user_id=payload.user_id,
            user_message=payload.message,
            summary=summary,
            continuity_notes=continuity,
            validated_signals=affective["validated_signals"],
        )
        STORE.append_episode(episode)
        STORE.append_risk_event(
            RiskEvent(
                user_id=payload.user_id,
                inferred_risk_level=safety.inferred_risk_level,
                escalation_status=safety.escalation_status,
                matched_signals=safety.matched_signals,
            )
        )

        return OrchestratorOutput(
            affective_state=affective["affective_state"].model_dump(mode="json"),
            inferred_risk_level=safety.inferred_risk_level,
            continuity_notes=continuity,
            validated_signals=affective["validated_signals"],
            intervention_style=intervention.intervention_style,
            recommended_next_step=intervention.recommended_next_step,
            escalation_status=safety.escalation_status,
            safety_notes=safety.safety_notes,
            narrative_memory_reference=[item.summary for item in memory_refs],
            response_text=response_text,
        )

    def _compose_response(self, affective_summary: str, safety, intervention_style: str, next_step: str, continuity: str, archetype: str) -> str:
        if safety.escalation_status == "HIGH_RISK_ESCALATION":
            return (
                "Lo que cuentas sugiere un nivel de riesgo que no conviene sostener solo con apoyo digital. "
                "Lo mas importante ahora es que contactes de inmediato con una persona de confianza, un profesional de urgencias "
                "o el servicio de emergencias de tu zona. Si puedes, no te quedes a solas mientras pides ayuda."
            )
        return (
            f"Estoy leyendo malestar compatible con {affective_summary.lower()}. "
            f"Mantengo continuidad con tu proceso: {continuity}. "
            f"La intervencion seleccionada es {intervention_style}. "
            f"Siguiente paso recomendado: {next_step}. "
            f"Nota simbolica con valor auxiliar: {archetype}"
        )


ORCHESTRATOR = PsychologicalOrchestrator()
