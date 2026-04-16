# Apollo Policy Enforcer Agent

Agente API-first para enforcement determinista de politicas corporativas. Traduce lenguaje natural a intencion tipada, compila predicates, valida estado simbolico y autoriza o bloquea acciones con trazabilidad completa.

## API

- `GET /api/health`
- `POST /api/enforce`
- `POST /api/validate`
- `GET /api/mandates/{mandate_id}`
- `GET /api/audit/{reference}`
- `GET /api/policies/{policy_id}`
