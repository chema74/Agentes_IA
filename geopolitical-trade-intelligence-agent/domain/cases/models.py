from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from domain.country_risk.models import CountryRiskProfile
from domain.exposure.models import TradeExposureMap
from domain.routes.models import RouteDisruptionAlert
from domain.sanctions.models import SanctionEvent
from domain.signals.models import GeopoliticalSignal


class HumanReviewGate(BaseModel):
    status: str
    owner: str
    rationale: str


class DecisionMemorandum(BaseModel):
    summary: str
    confidence: float


class TradeCase(BaseModel):
    case_id: str
    estado_de_la_señal_geopolítica: str
    resumen_del_perfil_de_riesgo_país: CountryRiskProfile
    mapa_de_exposición_comercial: TradeExposureMap
    eventos_de_sanción_o_restricción_detectados: list[SanctionEvent] = Field(default_factory=list)
    alertas_de_disrupción_de_ruta: list[RouteDisruptionAlert] = Field(default_factory=list)
    nivel_de_riesgo_internacional: str
    escenarios_relevantes: list[str] = Field(default_factory=list)
    recomendación_operativa: str
    revisión_humana_requerida: bool
    estado_de_la_puerta_de_revisión_humana: HumanReviewGate
    memorando_de_decisión_exportadora: DecisionMemorandum
    referencia_de_auditoría: str
    señales: list[GeopoliticalSignal] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
