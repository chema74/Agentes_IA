# Portfolio IA Aplicada

Repositorio monorepo con una web pública en la raíz y una colección de agentes y prototipos de IA orientados a negocio.

## Mapa rápido

- `proyectos/`: prototipos y bases públicas del portfolio.
- `a2a-self-healing-logistics-agent/`: agente autónomo de logística y negociación.
- `agentic-learning-integrity-orchestrator/`: orquestador de integridad del aprendizaje.
- `apollo-policy-enforcer-agent/`: agente de enforcement simbólico de políticas.
- `audit-compliance-evidence-agent/`: sistema de auditoría y evidencias.
- `autonomous-legal-counsel-agent/`: agente legal API-first.
- `change-process-coaching-orchestrator/`: orquestador de cambio organizativo.
- `contract-obligations-agent/`: agente de revisión contractual y obligaciones.
- `geopolitical-trade-intelligence-agent/`: agente de inteligencia geopolítica y comercial.
- `nspa-psychological-orchestrator/`: orquestador de apoyo psicológico estructurado.

## Estado del repositorio

- La web pública vive en la raíz (`index.html`, `proyectos.html`, etc.).
- El código ejecutable principal vive en las carpetas de agente y en `proyectos/`.
- Hay una CI mínima que valida estructura y compilación Python.
- El repositorio todavía mezcla productos maduros con prototipos de portfolio.

## Catálogo

La visión consolidada, el estado por proyecto y la propuesta de ordenación están en [CATALOGO.md](CATALOGO.md).

## Estructura real

```text
Agentes_IA/
├── index.html
├── proyectos.html
├── README.md
├── CATALOGO.md
├── assets/
├── core/
├── proyectos/
│   ├── p01-inteligencia-comercial-internacional
│   ├── p02-agente-multi-herramienta
│   ├── p03-agente-licitaciones
│   ├── p04-agente-rrhh-candidatos
│   ├── p05-rag-documentacion-interna
│   ├── p06-rag-contratos-legales
│   ├── p07-chatbot-atencion-cliente
│   ├── p08-rag-normativa-comercio
│   ├── p9-evaluador-ideas-negocio
│   └── p10-dashboard-lenguaje-natural
├── a2a-self-healing-logistics-agent/
├── agentic-learning-integrity-orchestrator/
├── apollo-policy-enforcer-agent/
├── audit-compliance-evidence-agent/
├── autonomous-legal-counsel-agent/
├── change-process-coaching-orchestrator/
├── contract-obligations-agent/
├── geopolitical-trade-intelligence-agent/
├── nspa-psychological-orchestrator/
├── scripts/
└── tests/
```

## Calidad y CI

Ejecución local de los checks:

```bash
.venv\Scripts\python scripts/ci_lint.py
.venv\Scripts\python scripts/ci_smoke.py
```

Workflow GitHub Actions:

- `.github/workflows/ci.yml`
- jobs `lint` y `smoke` con Python 3.11

## Política de repositorio

- No versionar secretos (`.env`) ni artefactos de runtime (`sqlite`, `chroma_db`, `outputs`, `logs`, `site-packages`).
- Mantener `README.md` coherentes por proyecto.
- Mantener un entrypoint claro por carpeta.
- Reservar `proyectos/` para piezas de portfolio y dejar el resto para agentes más completos.

