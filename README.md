# Portfolio IA Aplicada

Repositorio monorepo con una web publica en la raiz y una coleccion de agentes y prototipos de IA orientados a negocio.

## Mapa rapido

- `portfolio/`: prototipos y bases publicas del portfolio.
- `products/`: agentes y orquestadores mas maduros.
- `core/`: utilidades compartidas.

## Estado del repositorio

- La web publica vive en la raiz (`index.html`, `proyectos.html`, etc.).
- El codigo ejecutable principal vive en `portfolio/` y `products/`.
- Hay una CI minima que valida estructura y compilacion Python.
- El repositorio ya separa fisicamente demos y agentes de producto.

## Catalogo

La vision consolidada, el estado por proyecto y la propuesta de ordenacion estan en [CATALOGO.md](CATALOGO.md).

## Estructura real

```text
Agentes_IA/
├── index.html
├── proyectos.html
├── README.md
├── CATALOGO.md
├── assets/
├── core/
├── portfolio/
│   ├── p01-inteligencia-comercial-internacional
│   ├── p02-agente-multi-herramienta
│   ├── p03-agente-licitaciones
│   ├── p04-agente-rrhh-candidatos
│   ├── p05-rag-documentacion-interna
│   ├── p06-rag-contratos-legales
│   ├── p07-chatbot-atencion-cliente
│   ├── p08-rag-normativa-comercio
│   ├── p09-evaluador-ideas-negocio
│   └── p10-dashboard-lenguaje-natural
├── products/
│   ├── a2a-self-healing-logistics-agent
│   ├── agentic-learning-integrity-orchestrator
│   ├── apollo-policy-enforcer-agent
│   ├── audit-compliance-evidence-agent
│   ├── autonomous-legal-counsel-agent
│   ├── change-process-coaching-orchestrator
│   ├── contract-obligations-agent
│   ├── geopolitical-trade-intelligence-agent
│   └── nspa-psychological-orchestrator
├── scripts/
└── tests/
```

## Calidad y CI

Ejecucion local de los checks:

```bash
.venv\Scripts\python scripts/ci_lint.py
.venv\Scripts\python scripts/ci_smoke.py
```

Workflow GitHub Actions:

- `.github/workflows/ci.yml`
- jobs `lint` y `smoke` con Python 3.11

## Politica de repositorio

- No versionar secretos (`.env`) ni artefactos de runtime (`sqlite`, `chroma_db`, `outputs`, `logs`, `site-packages`).
- Mantener `README.md` coherentes por proyecto.
- Mantener un entrypoint claro por carpeta.
- Reservar `portfolio/` para piezas de portfolio y `products/` para agentes mas completos.

