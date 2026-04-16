# Arquitectura

## Capas

- `app`: API FastAPI para evaluar y ejecutar recuperaciones.
- `core`: configuracion, logging, auditoria y safety breaker.
- `domain`: modelos de tareas, agent cards, subastas, planes, negociacion y auditoria.
- `agents`: capacidades especializadas invocadas por el orquestador.
- `services`: adapters reales para A2A, MCP, Groq y storage operativo.
- `tests`: unitarias, de integracion y safety.

## Runtime

`disruption_monitor -> peer_discovery_engine -> negotiation_swarm -> sla_guardian -> logistics_circuit_breaker -> recovery_executor`
