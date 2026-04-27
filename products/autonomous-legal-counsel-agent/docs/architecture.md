# Arquitectura

## Capas

- `app`: API FastAPI para review, redlining y negociacion.
- `core`: configuracion, logging, auditoria, bootstrap SQL y legal breaker.
- `domain`: contratos, clausulas, riesgos, templates, redlines y negociacion.
- `agents`: nodos del runtime contractual.
- `services`: adapters para Gemini, A2A, playbooks, templates y storage.
- `tests`: unitarias, integracion y safety.

## Runtime

`document_intake_clerk -> clause_extraction_engine -> risk_scoring_analyst -> a2a_negotiation_counsel -> final_approval_governor -> legal_risk_circuit_breaker`
