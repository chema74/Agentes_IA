"""
domain/schemas.py
Responsabilidad: Modelos de datos estrictos para validación y persistencia.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AnalisisNarrativoLLM(BaseModel):
    resumen_ejecutivo: str
    analisis_detallado: Dict[str, str]
    recomendaciones: List[str]
    puntos_clave: List[str]
    limitaciones: Optional[str] = None


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
