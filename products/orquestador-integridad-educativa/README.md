# orquestador-integridad-educativa

Sistema multiagente para proteger la integridad del aprendizaje, reconstruir evidencia formativa y devolver al docente control real sobre la evaluacion asistida por IA.

## Objetivo

Distinguir entre progreso genuino, ayuda legitima, dependencia improductiva de IA, incoherencias de autoria y necesidad de revision academica formal.

## Stack objetivo

- Python 3.11
- FastAPI
- Supabase
- LangGraph
- Upstash Redis
- Neon Postgres + pgvector
- Pydantic v2
- LangSmith
- Gemini 1.5 Pro

## Arranque local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m pytest
```

## Contrato de salida

Siempre devuelve:
- estado_del_objetivo_de_aprendizaje
- resumen_de_traza_de_evidencia
- estado_del_evento_de_evaluacion
- nivel_de_senal_de_integridad
- incoherencias_detectadas
- puntuacion_de_confianza
- plan_de_retroalimentacion
- intervencion_recomendada
- revision_docente_requerida
- estado_de_anulacion_docente
- recomendacion_final
- referencia_de_auditoria
