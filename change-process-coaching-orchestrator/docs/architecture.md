# Arquitectura

## Capas

- `app`: API FastAPI para evaluacion e intervencion.
- `core`: configuracion, logging, auditoria, bootstrap SQL y circuit breaker.
- `domain`: senales, resistencia, friccion, stakeholders, intervenciones, hitos y puerta de supervision.
- `agents`: etapas del runtime de cambio.
- `services`: adapters para Groq, Gemini, LangSmith y storage.
- `tests`: unitarias, integracion y safety.

## Runtime

`registrador_de_senales_de_cambio -> analizador_de_friccion_organizativa_y_personal -> mapeador_de_stakeholders_o_contexto_individual -> planificador_de_intervencion_de_cambio -> gobernador_de_supervision_de_transformacion -> change_process_circuit_breaker`
