# Arquitectura

## Capas

- `app`: API FastAPI para validacion y enforcement.
- `core`: configuracion, logging, auditoria, Policy Circuit Breaker y bootstrap SQL.
- `domain`: intenciones, predicates, estado simbolico, trazas y mandatos.
- `agents`: etapas del runtime de enforcement.
- `services`: adapters para SambaNova, repositorio de politicas, estado y auditoria.
- `tests`: unitarias, integracion y safety.

## Runtime

`natural_language_intent_encoder -> predicate_compiler -> symbolic_state_validator -> policy_enforcement_gate -> policy_circuit_breaker -> deterministic_decoder`

## Persistencia

- `action_mandates`, `validation_traces`, `audit_events` e `idempotency_keys` persisten en SQL.
- En local se usa SQLite via `NEON_DATABASE_URL=sqlite:///...`.
- La forma del esquema esta preparada para migrarse a Postgres/Neon sin tocar el dominio.
