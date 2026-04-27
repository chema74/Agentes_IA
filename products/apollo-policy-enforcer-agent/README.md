# Apollo Policy Enforcer Agent

Agente API-first para enforcement determinista de politicas corporativas. Traduce lenguaje natural a intencion tipada, compila predicates, valida estado simbolico y autoriza o bloquea acciones con trazabilidad completa.

## Operacion

- autenticacion por `X-API-Key`
- idempotencia de enforcement por `X-Idempotency-Key`
- persistencia SQL de mandatos, trazas e idempotencia
- inicializacion de esquema en `core/db/sql/001_init_schema.sql`
- modo local sobre SQLite a traves de `NEON_DATABASE_URL=sqlite:///...`

## API

- `GET /api/health`
- `POST /api/enforce`
- `POST /api/validate`
- `GET /api/mandates/{mandate_id}`
- `GET /api/audit/{reference}`
- `GET /api/policies/{policy_id}`
