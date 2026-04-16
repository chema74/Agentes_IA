# Operaciones

## Objetivo

Este documento resume el minimo operativo para poner el servicio en staging o produccion controlada.

## Variables recomendadas por entorno

### Staging

- `APP_ENV=staging`
- `REQUIRE_API_KEY=true`
- `ENABLE_RATE_LIMIT=true`
- `RATE_LIMIT_REQUESTS=60`
- `RATE_LIMIT_WINDOW_SECONDS=60`
- `STORAGE_BACKEND=supabase` si ya existe tabla gestionada externamente
- `CACHE_BACKEND=upstash` si quieres validar latencia y wiring real
- `VECTOR_BACKEND=neon` solo cuando pgvector este provisionado

### Produccion

- `APP_ENV=production`
- `REQUIRE_API_KEY=true`
- `ENABLE_RATE_LIMIT=true`
- `STORAGE_BACKEND=supabase`
- `CACHE_BACKEND=upstash`
- `VECTOR_BACKEND=neon`

## Smoke check operativo

Antes de exponer el servicio:

```powershell
..\.venv\Scripts\python.exe .\scripts\smoke_storage.py
```

Debe verificar:

- `health.case_store.status`
- `health.cache_store.status`
- `health.vector_store.status`
- `roundtrip.case_saved`
- `roundtrip.audit_events`

## Checklist de despliegue

- confirmar `SERVICE_API_KEY` no vacia y gestionada por secreto
- confirmar backend principal accesible desde el entorno
- ejecutar `GET /api/health`
- ejecutar `scripts/smoke_storage.py`
- validar que `X-Request-ID` vuelve en respuestas
- validar `429` cuando rate limiting este activado
- revisar logs JSON y request ids en el agregador

## Incidencias esperables

- si falla `case_store`, el servicio no debe considerarse listo
- si falla `cache_store`, el servicio puede seguir en modo degradado
- si falla `vector_store`, la evaluacion principal sigue siendo valida pero sin indexacion semantica
