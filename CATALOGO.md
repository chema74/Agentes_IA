# Catalogo del Monorepo

Este documento resume que hay en `Agentes_IA`, que esta terminado, que esta en progreso y que falta para que el conjunto quede mas limpio y presentable.

## Lectura ejecutiva

Hay tres grupos claros:

- `proyectos/`: prototipos y bases publicas del portfolio.
- agentes y orquestadores grandes: productos con bastante profundidad tecnica.
- utilidades compartidas: `core/`, `scripts/`, `tests/`, `.github/`.

La principal deuda no es solo de codigo. Es de orden:

- nombres no del todo homogeneos,
- documentacion desigual,
- mezcla de madurez entre carpetas,
- poca señal visual de que esta listo y que no.

## Estado por proyecto

| Proyecto | Estado | Que falta | Prioridad |
|---|---|---|---|
| `proyectos/p01-inteligencia-comercial-internacional` | Muy avanzado | Pulido de producto, normalizar docs, reforzar narrativa demo -> produccion | Media |
| `proyectos/p02-agente-multi-herramienta` | Prototipo | Cierre funcional y mas documentacion | Media |
| `proyectos/p03-agente-licitaciones` | Prototipo | Consolidar flujo, tests y posicionamiento | Media |
| `proyectos/p04-agente-rrhh-candidatos` | Prototipo | Mayor cierre funcional y narrativa | Media |
| `proyectos/p05-rag-documentacion-interna` | Prototipo | Mas definicion de alcance y robustez | Media |
| `proyectos/p06-rag-contratos-legales` | Prototipo | Aterrizar alcance y diferenciarlo del agente legal serio | Media |
| `proyectos/p07-chatbot-atencion-cliente` | Prototipo | Mas estructura de producto y validacion | Baja |
| `proyectos/p08-rag-normativa-comercio` | Prototipo | Mejorar historia de uso y acabados | Media |
| `proyectos/p09-evaluador-ideas-negocio` | Prototipo | Consolidar branding y docs | Media |
| `proyectos/p10-dashboard-lenguaje-natural` | Prototipo | Convertirlo en demo clara y mas consistente | Baja |
| `a2a-self-healing-logistics-agent` | Avanzado | Operacion, documentacion y empaquetado final | Alta |
| `agentic-learning-integrity-orchestrator` | Avanzado | Mas cierre de producto y endurecimiento | Alta |
| `apollo-policy-enforcer-agent` | Avanzado | Casos de uso cerrados, validacion y hardening | Alta |
| `audit-compliance-evidence-agent` | Muy avanzado | Mejor despliegue real y UX mas cuidada | Media |
| `autonomous-legal-counsel-agent` | Base solida | Mas documentacion, pruebas y cierre funcional | Alta |
| `change-process-coaching-orchestrator` | Muy avanzado | Consolidar runtime, persistencia y observabilidad | Media |
| `contract-obligations-agent` | Muy avanzado | Conectores reales, produccion cerrada y UX/operacion | Media |
| `geopolitical-trade-intelligence-agent` | Avanzado | Completar producto, docs y acabados de API | Alta |
| `nspa-psychological-orchestrator` | Avanzado | Seguridad, continuidad narrativa y experiencia de uso | Alta |

## Que falta en global

- Un indice central por proyecto con estado, entrypoint y siguiente paso.
- Una separacion mas clara entre demo/portfolio y agentes de producto.
- Nombres homogeneos en carpetas y README.
- Mas consistencia entre documentacion publica y madurez tecnica.
- Mas señal de operacion: despliegue, observabilidad, variables de entorno y runbooks.

## Inconsistencias concretas

- `p9-evaluador-ideas-negocio` ya no existe: quedo normalizado como `p09-evaluador-ideas-negocio`.
- Ya no deberia haber mezcla de `README.md` y `readme.md`.
- La documentacion raiz habla de 10 lineas de agente, pero no diferencia bien que esta listo y que es prototipo.
- Varios proyectos tienen buena arquitectura interna, pero no una historia de producto igual de solida.

## Estructura recomendada

```text
Agentes_IA/
├── public/                   # web publica y marketing
├── portfolio/               # prototipos y demos
├── products/                # agentes mas maduros
├── shared/                  # utilidades comunes reales
├── archive/                 # prototipos retirados o antiguos
├── docs/                    # catalogo y decisiones transversales
├── scripts/
└── tests/
```

### Si no quieres mover todo todavia

Una reorganizacion intermedia mas conservadora seria:

```text
Agentes_IA/
├── proyectos/               # mantener demos aqui
├── agentes/                 # mover los sistemas grandes aqui
├── core/                    # helpers compartidos reales
├── docs/
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

