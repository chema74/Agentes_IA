# Change Process Coaching Orchestrator

Orquestador API-first para registrar senales de cambio, detectar friccion, mapear stakeholders, disenar intervencion proporcional y activar supervision humana cuando el caso deja de ser automatizable de forma responsable.

No es un chatbot motivacional. Es una capa operativa para hacer visible la friccion real del cambio y devolver una lectura estructurada del proceso.

## Que hace

- ingiere notas, sesiones, tareas, encuestas y senales explicitas
- clasifica senales de cambio y perfila resistencia
- detecta bloqueos de adopcion, fatiga y gap entre discurso y ejecucion
- genera un plan de intervencion secuenciado
- evalua si el caso puede seguir automatizandose o si debe pasar a supervision humana
- registra auditoria y permite persistencia con modo local o backends externos

## API

- `GET /api/health`
- `POST /api/change-cases/evaluate`
- `POST /api/change-cases/intervene`
- `GET /api/change-cases/{case_id}`
- `GET /api/audit/{reference}`

## Contrato de salida

Toda evaluacion e intervencion devuelve estos campos:

- `estado_del_proceso_de_cambio`
- `resumen_de_senales_detectadas`
- `mapa_de_stakeholders_o_contexto_personal`
- `perfil_de_resistencia`
- `bloqueos_de_adopcion_detectados`
- `nivel_de_friccion`
- `plan_de_intervencion`
- `hitos_de_transformacion`
- `alerta_de_fatiga_de_cambio`
- `revision_humana_requerida`
- `estado_de_la_puerta_de_supervision_humana`
- `recomendacion_final`
- `referencia_de_auditoria`
- `case_id`

## Runtime actual

El servicio dispone de dos caminos compatibles:

- `ChangeProcessCoachingOrchestrator`: flujo heuristico principal expuesto por API
- `graph_runtime`: runtime LangGraph multi-nodo con estado explicito

El runtime LangGraph ya modela esta secuencia:

`signal_recorder -> friction_analyzer -> stakeholder_mapper -> intervention_planner -> supervision_governor -> finalizer`

## Storage

La persistencia esta desacoplada por backend:

- store principal: `local` o `supabase`
- cache: `memory` o `upstash`
- vector store: `local/noop` o `neon`

La politica es deliberadamente tolerante a fallos:

- si falla el store principal, el caso falla
- si falla cache o vector store, el caso principal sigue adelante

## Variables principales

- `STORAGE_BACKEND=local|supabase`
- `CACHE_BACKEND=memory|upstash`
- `VECTOR_BACKEND=local|neon`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`
- `NEON_DATABASE_URL`

## Verificacion local

```powershell
..\.venv\Scripts\python.exe -m pytest -q
```

Consulta [docs/api.md](C:/Users/txema/Documents/Agentes_IA/orquestador-coaching-cambio/docs/api.md) y [docs/architecture.md](C:/Users/txema/Documents/Agentes_IA/orquestador-coaching-cambio/docs/architecture.md) para el detalle funcional.
