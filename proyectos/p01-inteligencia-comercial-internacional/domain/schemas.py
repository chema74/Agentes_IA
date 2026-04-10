"""
domain/schemas.py
Responsabilidad: contratos de datos estrictos y reutilizables del proyecto.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ============================================================
# 1. CONTRATO CANONICO DEL ANALISIS NARRATIVO
# ============================================================

NARRATIVE_REQUIRED_KEYS = (
    "pais",
    "resumen_ejecutivo",
    "alertas",
    "oportunidades",
)


def get_narrative_json_contract() -> str:
    """
    Devuelve el contrato oficial en texto para reutilizarlo en prompts.
    """
    return """
{
  "pais": "string",
  "resumen_ejecutivo": "string",
  "alertas": ["string", "string", "string"],
  "oportunidades": ["string", "string", "string"]
}
""".strip()


class AnalisisNarrativoLLM(BaseModel):
    """
    Contrato narrativo oficial consumido por parser, app y exportadores.
    """

    pais: str
    resumen_ejecutivo: str
    alertas: List[str]
    oportunidades: List[str]

    @model_validator(mode="before")
    @classmethod
    def _normalizar_campos_legacy(cls, data: Any) -> Any:
        """
        Paso 1: admite aliases históricos mínimos sin duplicar contratos.
        """
        if not isinstance(data, dict):
            return data

        normalizado = dict(data)

        if "resumen" in normalizado and "resumen_ejecutivo" not in normalizado:
            normalizado["resumen_ejecutivo"] = normalizado["resumen"]

        if "riesgos" in normalizado and "alertas" not in normalizado:
            normalizado["alertas"] = normalizado["riesgos"]

        return normalizado

    @field_validator("pais", "resumen_ejecutivo")
    @classmethod
    def _validar_texto_obligatorio(cls, value: str) -> str:
        """
        Paso 2: obliga a que los campos narrativos principales tengan texto real.
        """
        text = str(value).strip()
        if not text:
            raise ValueError("El campo narrativo no puede estar vacío.")
        return text

    @field_validator("alertas", "oportunidades")
    @classmethod
    def _validar_listas_narrativas(cls, value: List[str]) -> List[str]:
        """
        Paso 3: limpia listas y exige exactamente tres elementos útiles.
        """
        items = [str(item).strip() for item in value if str(item).strip()]
        if len(items) != 3:
            raise ValueError("Cada lista narrativa debe incluir exactamente 3 elementos.")
        return items


# ============================================================
# 2. ESQUEMAS DE RANKING E HISTORIAL
# ============================================================

class SourceItem(BaseModel):
    category: str = ""
    title: str = ""
    url: str = ""
    summary: str = ""


class RankingMetadata(BaseModel):
    run_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    generated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sector: str = "General"
    company_type: str = "PYME"
    countries_requested: List[str] = Field(default_factory=list)
    total_countries: int = 0
    version: str = "1.0"


class RankingItem(BaseModel):
    position: int
    country: str
    score_total: float
    dimension_scores: Dict[str, float]
    executive_summary: str = ""
    sources: List[SourceItem] = Field(default_factory=list)
    raw_result: Dict[str, Any] = Field(default_factory=dict)


class RankingResult(BaseModel):
    metadata: RankingMetadata
    ranking: List[RankingItem]


__all__ = [
    "AnalisisNarrativoLLM",
    "NARRATIVE_REQUIRED_KEYS",
    "RankingItem",
    "RankingMetadata",
    "RankingResult",
    "SourceItem",
    "get_narrative_json_contract",
]
