# Arquitectura

## Capas

- `app`: API FastAPI para evaluacion de casos internacionales.
- `core`: configuracion, logging, auditoria, bootstrap SQL y circuit breaker.
- `domain`: señales, riesgo país, exposición comercial, sanciones, rutas y memorandos.
- `agents`: etapas del runtime de inteligencia internacional.
- `services`: adapters para Groq, Gemini, LangSmith y storage.
- `tests`: unitarias, integracion y safety.

## Runtime

`registrador_de_senales_geopoliticas -> interprete_de_politica_comercial -> analizador_de_exposicion_por_pais_y_sector -> mapeador_de_riesgo_logistico_y_de_ruta -> gobernador_de_decision_internacional -> geopolitical_trade_circuit_breaker`
