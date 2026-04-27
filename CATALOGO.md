# Catálogo del Monorepo

Este documento resume qué hay en la carpeta `Agentes_IA`, qué está terminado, qué está en progreso y qué falta para que el conjunto quede más limpio y presentable.

## Lectura ejecutiva

Hay tres grupos claros:

- `proyectos/`: prototipos y bases públicas del portfolio.
- agentes/orquestadores grandes: productos con bastante profundidad técnica.
- utilidades compartidas: `core/`, `scripts/`, `tests/`, `.github/`.

La principal deuda no es solo de código. Es de orden:

- nombres no del todo homogéneos,
- documentación desigual,
- mezcla de madurez entre carpetas,
- poca señal visual de qué está listo y qué no.

## Estado por proyecto

| Proyecto | Estado | Qué falta | Prioridad |
|---|---|---|---|
| `proyectos/p01-inteligencia-comercial-internacional` | Muy avanzado | Pulido de producto, normalizar docs, reforzar narrativa demo -> producción | Media |
| `proyectos/p02-agente-multi-herramienta` | Prototipo | Cierre funcional y más documentación | Media |
| `proyectos/p03-agente-licitaciones` | Prototipo | Consolidar flujo, tests y posicionamiento | Media |
| `proyectos/p04-agente-rrhh-candidatos` | Prototipo | Mayor cierre funcional y narrativa | Media |
| `proyectos/p05-rag-documentacion-interna` | Prototipo | Más definición de alcance y robustez | Media |
| `proyectos/p06-rag-contratos-legales` | Prototipo | Aterrizar alcance y diferenciarlo del agente legal serio | Media |
| `proyectos/p07-chatbot-atencion-cliente` | Prototipo | Más estructura de producto y validación | Baja |
| `proyectos/p08-rag-normativa-comercio` | Prototipo | Mejorar historia de uso y acabados | Media |
| `proyectos/p9-evaluador-ideas-negocio` | Prototipo | Normalizar nombre a `p09`, consolidar branding y docs | Media |
| `proyectos/p10-dashboard-lenguaje-natural` | Prototipo | Convertirlo en demo clara y más consistente | Baja |
| `a2a-self-healing-logistics-agent` | Avanzado | Operación, documentación y empaquetado final | Alta |
| `agentic-learning-integrity-orchestrator` | Avanzado | Más cierre de producto y endurecimiento | Alta |
| `apollo-policy-enforcer-agent` | Avanzado | Casos de uso cerrados, validación y hardening | Alta |
| `audit-compliance-evidence-agent` | Muy avanzado | Mejor despliegue real y UX más cuidada | Media |
| `autonomous-legal-counsel-agent` | Base sólida | Más documentación, pruebas y cierre funcional | Alta |
| `change-process-coaching-orchestrator` | Muy avanzado | Consolidar runtime, persistencia y observabilidad | Media |
| `contract-obligations-agent` | Muy avanzado | Conectores reales, producción cerrada y UX/operación | Media |
| `geopolitical-trade-intelligence-agent` | Avanzado | Completar producto, docs y acabados de API | Alta |
| `nspa-psychological-orchestrator` | Avanzado | Seguridad, continuidad narrativa y experiencia de uso | Alta |

## Qué falta en global

- Un índice central por proyecto con estado, entrypoint y siguiente paso.
- Una separación más clara entre demo/portfolio y agentes de producto.
- Nombres homogéneos en carpetas y README.
- Más consistencia entre documentación pública y madurez técnica.
- Más señal de operación: despliegue, observabilidad, variables de entorno y runbooks.

## Inconsistencias concretas

- `p9-evaluador-ideas-negocio` no sigue el patrón `p0X`.
- Hay mezcla de `README.md` y `readme.md`.
- La documentación raíz habla de 10 líneas de agente, pero no diferencia bien qué está listo y qué es prototipo.
- Varios proyectos tienen buena arquitectura interna, pero no una historia de producto igual de sólida.

## Estructura recomendada

```text
Agentes_IA/
├── public/                   # web pública y marketing
├── portfolio/                # prototipos y demos
├── products/                 # agentes más maduros
├── shared/                   # utilidades comunes reales
├── archive/                  # prototipos retirados o antiguos
├── docs/                     # catálogo y decisiones transversales
├── scripts/
└── tests/
```

### Si no quieres mover todo todavía

Una reorganización intermedia más conservadora sería:

```text
Agentes_IA/
├── proyectos/                # mantener demos aquí
├── agentes/                  # mover los sistemas grandes aquí
├── core/                     # helpers compartidos reales
├── docs/
├── scripts/
└── tests/
```

## Orden recomendado de limpieza

1. Normalizar nombres y README.
2. Añadir un estado visible por proyecto.
3. Separar demos de agentes de producto.
4. Unificar docs de arquitectura y despliegue.
5. Revisar qué proyectos pasan a `archive/`.

## Mi criterio de madurez

- `terminado`: producto defendible, docs claras, tests, entrypoint, packaging.
- `muy avanzado`: casi listo, pero falta pulido y operación.
- `avanzado`: buena base, todavía faltan cierres de producto.
- `prototipo`: útil como demo, pero aún no lo vendería como producto.

