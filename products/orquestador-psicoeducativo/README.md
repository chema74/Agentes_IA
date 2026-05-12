# orquestador-psicoeducativo

Sistema de apoyo emocional estructurado con memoria narrativa, inferencia afectiva prudente y escalado de seguridad para situaciones de riesgo.

## Principios

- apoyo emocional, no diagnostico cerrado
- continuidad narrativa entre episodios
- prudencia clinica
- escalado responsable ante riesgo
- trazabilidad de inferencias e intervenciones

## Stack objetivo

- Python 3.11
- FastAPI
- Supabase
- LangGraph
- Upstash Redis
- Neon + pgvector
- Gemini 1.5 Flash

## Arranque local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m pytest
```

## Documentacion

- `docs/architecture.md`
- `docs/data-model.md`
- `docs/safety-protocol.md`
- `docs/api.md`

## Limites

- no sustituye atencion profesional urgente
- no emite diagnosticos clinicos cerrados
- activa circuit breaker ante indicios de crisis
- toda inferencia debe entenderse como apoyo, no certeza clinica
