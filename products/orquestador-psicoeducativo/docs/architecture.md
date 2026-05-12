# Arquitectura

## Hub and spoke

El sistema se organiza alrededor de un orquestador central que coordina seis capacidades:

1. `affective_signal_interpreter`
2. `neuro_state_modeler`
3. `archetypal_mapper`
4. `cbt_intervention_guide`
5. `narrative_continuity_keeper`
6. `psychological_safety_circuit_breaker`

## Principio rector

La respuesta no se optimiza solo por tono. Se optimiza por seguridad, coherencia longitudinal y proporcionalidad frente al riesgo.

## Memoria

- estado caliente: Upstash Redis o store local de demostracion
- memoria narrativa y embeddings: Neon + pgvector o fallback local
- storage operativo y auth: Supabase o entorno mock
