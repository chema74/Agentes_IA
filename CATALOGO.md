# Catalogo del Monorepo

Este documento resume que hay en `Agentes_IA`, que esta terminado, que esta en progreso y que falta para que el conjunto quede mas limpio y presentable.

## Lectura ejecutiva

Hay tres grupos claros:

- `portfolio/`: prototipos y bases publicas del portfolio.
- `products/`: productos y orquestadores mas maduros.
- utilidades compartidas: `core/`, `scripts/`, `tests/`, `.github/`.

La principal deuda no es solo de codigo. Es de orden:

- nombres no del todo homogeneos,
- documentacion desigual,
- mezcla de madurez entre carpetas,
- poca señal visual de que esta listo y que no.

## Estado por proyecto

| Proyecto | Estado | Que falta | Prioridad |
|---|---|---|---|
| `portfolio/p01-inteligencia-comercial-internacional` | Muy avanzado | Pulido de producto, normalizar docs, reforzar narrativa demo -> produccion | Media |
| `portfolio/p02-agente-multi-herramienta` | Prototipo | Cierre funcional y mas documentacion | Media |
| `portfolio/p03-agente-licitaciones` | Prototipo | Consolidar flujo, tests y posicionamiento | Media |
| `portfolio/p04-agente-rrhh-candidatos` | Prototipo | Mayor cierre funcional y narrativa | Media |
| `portfolio/p05-rag-documentacion-interna` | Prototipo | Mas definicion de alcance y robustez | Media |
| `portfolio/p06-rag-contratos-legales` | Prototipo | Aterrizar alcance y diferenciarlo del agente legal serio | Media |
| `portfolio/p07-chatbot-atencion-cliente` | Prototipo | Mas estructura de producto y validacion | Baja |
| `portfolio/p08-rag-normativa-comercio` | Prototipo | Mejorar historia de uso y acabados | Media |
| `portfolio/p09-evaluador-ideas-negocio` | Prototipo | Consolidar branding y docs | Media |
| `portfolio/p10-dashboard-lenguaje-natural` | Prototipo | Convertirlo en demo clara y mas consistente | Baja |
| `products/a2a-self-healing-logistics-agent` | Avanzado | Operacion, documentacion y empaquetado final | Alta |
| `products/agentic-learning-integrity-orchestrator` | Avanzado | Mas cierre de producto y endurecimiento | Alta |
| `products/apollo-policy-enforcer-agent` | Avanzado | Casos de uso cerrados, validacion y hardening | Alta |
| `products/audit-compliance-evidence-agent` | Muy avanzado | Mejor despliegue real y UX mas cuidada | Media |
| `products/autonomous-legal-counsel-agent` | Base solida | Mas documentacion, pruebas y cierre funcional | Alta |
| `products/change-process-coaching-orchestrator` | Muy avanzado | Consolidar runtime, persistencia y observabilidad | Media |
| `products/contract-obligations-agent` | Muy avanzado | Conectores reales, produccion cerrada y UX/operacion | Media |
| `products/geopolitical-trade-intelligence-agent` | Avanzado | Completar producto, docs y acabados de API | Alta |
| `products/nspa-psychological-orchestrator` | Avanzado | Seguridad, continuidad narrativa y experiencia de uso | Alta |

## Priorizacion de products

| Proyecto | Score | Posicion | Siguiente paso |
|---|---:|---|---|
| `products/audit-compliance-evidence-agent` | 9.5 | 1 | Cerrar despliegue real, observabilidad y UX final |
| `products/contract-obligations-agent` | 9.0 | 2 | Consolidar conectores reales y empaquetado de produccion |
| `products/apollo-policy-enforcer-agent` | 8.7 | 3 | Endurecer validacion, permisos y casos de enforcement |
| `products/a2a-self-healing-logistics-agent` | 8.4 | 4 | Cerrar operacion de recovery y documentacion de runtime |
| `products/change-process-coaching-orchestrator` | 8.0 | 5 | Afinar persistencia, observabilidad y criterios de escalado |
| `products/geopolitical-trade-intelligence-agent` | 7.8 | 6 | Completar historia de producto y cerrar APIs visibles |
| `products/nspa-psychological-orchestrator` | 7.6 | 7 | Fortalecer seguridad, limites y continuidad narrativa |
| `products/agentic-learning-integrity-orchestrator` | 7.2 | 8 | Cerrar producto, casos docentes y trazabilidad de evidencia |
| `products/autonomous-legal-counsel-agent` | 7.0 | 9 | Amplificar docs, tests y ruta de produccion |

## Que falta en global

- Un indice central por proyecto con estado, entrypoint y siguiente paso.
- Una separacion mas clara entre demo/portfolio y agentes de producto.
- Nombres homogeneos en carpetas y README.
- Mas consistencia entre documentacion publica y madurez tecnica.
- Mas señal de operacion: despliegue, observabilidad, variables de entorno y runbooks.

## Inconsistencias concretas

- `p09-evaluador-ideas-negocio` ya esta normalizado y sigue el patron `p0X`.
- Ya no deberia haber mezcla de `README.md` y `readme.md`.
- La documentacion raiz habla de 10 lineas de agente, pero no diferencia bien que esta listo y que es prototipo.
- Varios proyectos tienen buena arquitectura interna, pero no una historia de producto igual de solida.

## Estructura recomendada

```text
Agentes_IA/
├── index.html
├── proyectos.html
├── README.md
├── CATALOGO.md
├── assets/
├── core/
├── portfolio/
├── products/
├── scripts/
└── tests/
```

## Orden recomendado de limpieza

1. Normalizar nombres y README.
2. Anadir un estado visible por proyecto.
3. Separar demos de agentes de producto.
4. Unificar docs de arquitectura y despliegue.
5. Revisar que proyectos pasan a `archive/`.

## Mi criterio de madurez

- `terminado`: producto defendible, docs claras, tests, entrypoint, packaging.
- `muy avanzado`: casi listo, pero falta pulido y operacion.
- `avanzado`: buena base, todavia faltan cierres de producto.
- `prototipo`: util como demo, pero aun no lo venderia como producto.
