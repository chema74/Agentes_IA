# Arquitectura

El sistema usa un patron hub-and-spoke con LangGraph.

## Spokes

1. registrador de evidencia de aprendizaje
2. analizador de senales de integridad
3. motor de razonamiento evaluativo
4. planificador de retroalimentacion e intervencion
5. gobernador de supervision docente
6. circuit breaker de integridad

## Principio rector

No automatizar el cierre evaluativo cuando la evidencia es insuficiente, incoherente o no trazable.
