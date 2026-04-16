from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from domain.friction.models import AdoptionBlocker, FrictionAssessment
from domain.interventions.models import InterventionPlan
from domain.progress.models import ChangeFatigueAlert, HumanSupervisionGate, TransformationMilestone
from domain.resistance.models import ResistanceProfile
from domain.signals.models import ChangeSignal
from domain.stakeholders.models import StakeholderEntry


class IntakeSourceRef(BaseModel):
    source_type: str
    source_id: str = ""
    description: str = ""


class ChangeSessionNote(BaseModel):
    summary: str
    source: str = "session_note"
    sentiment: str = "neutral"


class ChangeTaskRecord(BaseModel):
    title: str
    status: str
    owner: str = ""
    due_window: str = ""


class SurveySignalInput(BaseModel):
    prompt: str
    response: str
    score: float | None = None


class Recommendation(BaseModel):
    summary: str
    level: int
    rationale: str
    automation_mode: str = "monitoring"
    next_best_owner: str = "lider_del_proceso"


class ChangeCase(BaseModel):
    case_id: str
    estado_del_proceso_de_cambio: str
    resumen_de_senales_detectadas: list[ChangeSignal] = Field(default_factory=list)
    mapa_de_stakeholders_o_contexto_personal: list[StakeholderEntry] = Field(default_factory=list)
    perfil_de_resistencia: ResistanceProfile
    bloqueos_de_adopcion_detectados: list[AdoptionBlocker] = Field(default_factory=list)
    nivel_de_friccion: FrictionAssessment
    plan_de_intervencion: InterventionPlan
    hitos_de_transformacion: list[TransformationMilestone] = Field(default_factory=list)
    alerta_de_fatiga_de_cambio: ChangeFatigueAlert
    revision_humana_requerida: bool
    estado_de_la_puerta_de_supervision_humana: HumanSupervisionGate
    recomendacion_final: Recommendation
    referencia_de_auditoria: str = Field(serialization_alias="referencia_de_auditor\u00eda")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
