# Arquitectura

## Capas

- `app`: API FastAPI y dependencias de acceso
- `core`: configuracion, logging, auditoria, seguridad de breaker y bootstrap DB
- `domain`: modelos de senales, friccion, resistencia, stakeholders, intervencion, progreso y caso
- `agents`: funciones de analisis y decision del flujo de cambio
- `services/orchestration`: orchestrator clasico y runtime LangGraph
- `services/storage`: persistencia principal, cache y vector store
- `services/llm`: clientes Groq y Gemini
- `tests`: unitarios, integracion y safety

## Runtime de cambio

### Camino clasico

`ChangeProcessCoachingOrchestrator` ejecuta:

1. captura de senales
2. analisis de friccion
3. mapeo de stakeholders
4. planificacion de intervencion
5. evaluacion de breaker
6. decision de supervision
7. ensamblado del caso y auditoria

### Camino LangGraph

`services/orchestration/graph_runtime.py` implementa un grafo multi-nodo real con estado explicito:

1. `signal_recorder`
2. `friction_analyzer`
3. `stakeholder_mapper`
4. `intervention_planner`
5. `supervision_governor`
6. `finalizer`

El estado del grafo conserva:

- entrada original del caso
- senales capturadas
- resistencia, bloqueos, friccion y fatiga
- stakeholders mapeados
- plan de intervencion
- breaker, puerta de supervision, hitos y recomendacion
- caso persistido y salida final

## Circuit Breaker

El breaker se activa cuando la automatizacion deja de ser proporcional o fiable. Actualmente eleva a nivel 4 si aparece alguna de estas combinaciones:

- baja confianza diagnostica
- fatiga alta
- bloqueo de adopcion critico
- gap alto entre discurso y ejecucion
- conversacion dificil pendiente
- resistencia de tipo `interpersonal_conflict` u `overload` con intensidad alta

### Escala de respuesta

- Nivel 1 `observation`: seguimiento ligero
- Nivel 2 `relevant_friction`: intervencion especifica y monitorizacion
- Nivel 3 `change_compromised`: proceso comprometido, revision humana
- Nivel 4 `circuit_breaker`: detener automatizacion fuerte y escalar

## Persistencia

La capa `StorageRuntime` compone tres responsabilidades:

- `case_store`: persistencia principal del caso y auditoria
- `cache_store`: acceso rapido a casos
- `vector_store`: indexacion opcional para recuperacion semantica

### Backends disponibles

- principal:
  `local` -> SQLite/Neon via `core.db.session`
  `supabase` -> REST API de Supabase
- cache:
  `memory` -> diccionario en proceso
  `upstash` -> REST API de Upstash Redis
- vector:
  `local` -> noop
  `neon` -> tabla `change_case_vectors` con `pgvector`

## Estrategia LLM

- Groq: clasificacion de senales y procesamiento frecuente
- Gemini: profundidad opcional para casos largos o delicados

## Criterio de robustez

- el flujo principal no depende de cache ni vector store
- la API devuelve siempre el mismo contrato, con o sin backends externos
- el storage principal sigue siendo la unica dependencia dura para operaciones de intervencion persistente
