# Catalogo del Monorepo

Este documento resume el estado real de `Agentes_IA` y lo que queda para cerrar el repositorio como entrega presentable.

## Resumen ejecutivo

El repositorio esta funcional: la estructura pasa lint, el smoke test compila 607 archivos Python, los tests minimos del portfolio pasan y los tests de `products/` pasan cuando se ejecutan por producto.

Lo que falta no es tanto hacer que funcione, sino cerrar limpieza, narrativa, documentacion y operacion.

## Estado por area

| Area | Estado | Pendiente principal |
|---|---|---|
| Web raiz | Funcional | Mantener copy final y evolucionar canal de contacto si se publica fuera de GitHub |
| `portfolio/` | Funcional como demo | Pulido editorial y cierre de `p05`, `p06`, `p08`, `p09`, `p10` |
| `products/` | Cerrado tecnicamente | Documentacion de despliegue, observabilidad y limites de dominio |
| `core/` | Estable | Reducir efectos al importar configuracion |
| `scripts/` | Operativo | Mantener runner global de productos |
| `tests/` | Verde | Ampliar cobertura solo si se endurece portfolio |

## Portfolio

| Proyecto | Estado | Que falta |
|---|---|---|
| `p01-inteligencia-comercial-internacional` | Cerrado tecnicamente | Pulido narrativo y demo final |
| `p02-agente-multi-herramienta` | Prototipo funcional | Definir mejor valor diferencial |
| `p03-agente-licitaciones` | Prototipo solido | Posicionamiento y README mas claro |
| `p04-agente-rrhh-candidatos` | Prototipo solido | Limpieza editorial menor |
| `p05-rag-documentacion-interna` | Funcional | Pulir textos e iconos residuales |
| `p06-rag-contratos-legales` | Funcional | Diferenciarlo del producto legal serio |
| `p07-chatbot-atencion-cliente` | Simple y estable | Mejor onboarding y limites |
| `p08-rag-normativa-comercio` | Funcional | Pulir textos y narrativa |
| `p09-evaluador-ideas-negocio` | Funcional | Corregir branding residual y enlace GitHub |
| `p10-dashboard-lenguaje-natural` | Funcional | Pulir textos de seguridad y demo |

## Products

| Proyecto | Estado tecnico | Cautela |
|---|---|---|
| `a2a-self-healing-logistics-agent` | Cerrado | Operacion y runbook |
| `apollo-policy-enforcer-agent` | Cerrado | Validacion de permisos y enforcement |
| `geopolitical-trade-intelligence-agent` | Cerrado | Riesgo de dominio y frescura de datos |
| `contract-obligations-agent` | Cerrado | Conectores reales y operacion |
| `autonomous-legal-counsel-agent` | Cerrado | Dominio legal sensible |
| `nspa-psychological-orchestrator` | Cerrado tecnicamente | Dominio psicologico sensible |
| `audit-compliance-evidence-agent` | Cerrado | Despliegue y UX final |
| `agentic-learning-integrity-orchestrator` | Cerrado tecnicamente | Contexto educativo sensible |
| `change-process-coaching-orchestrator` | Cerrado tecnicamente | Dominio organizacional sensible |

## Pendiente global

1. Terminar limpieza editorial en web y portfolio.
2. Revisar `core/config/settings.py` para evitar validaciones fuertes al importar.
3. Mantener fuera del repo artefactos locales: `.pytest-tmp/`, `.pytest_cache/`, `data/`, `exports/`, `.venv/`.
4. Documentar despliegue y variables de entorno por producto si se van a publicar.
