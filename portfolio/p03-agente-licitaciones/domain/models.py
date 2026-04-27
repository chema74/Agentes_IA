from pydantic import BaseModel, Field
from typing import List, Optional

class CriterioPuntuacion(BaseModel):
    criterio: str
    peso_pct: Optional[float] = None

class AnalisisLicitacion(BaseModel):
    titulo_licitacion: str
    organismo_convocante: str
    presupuesto_base: str
    plazo_ejecucion: str
    fecha_presentacion: str
    puntuacion_viabilidad: int = Field(..., ge=1, le=10)
    recomendacion: str
    requisitos_tecnicos: List[str]
    requisitos_economicos: List[str]
    criterios_puntuacion: List[CriterioPuntuacion]
    riesgos: List[str]
    fortalezas_candidato: List[str]
    resumen_ejecutivo: str
    proximos_pasos: List[str]
