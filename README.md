# Portfolio IA Aplicada

Repositorio de portfolio con web pública + subproyectos de agentes IA orientados a negocio.

## Estado actual del repo

- La web pública está en la raíz (`index.html`, `proyectos.html`, etc.).
- El código ejecutable está en `proyectos/`.
- Hay 10 líneas de agente a nivel portfolio, pero no todas tienen base pública dedicada en esta copia.
- CI mínima activa con dos checks:
  - `scripts/ci_lint.py` (coherencia estructura/README por proyecto)
  - `scripts/ci_smoke.py` (compilación Python)

## Estructura real

```text
Agentes_IA/
├── index.html
├── proyectos.html
├── README.md
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
├── scripts/
└── .github/workflows/ci.yml
```

Nota: `p9-evaluador-ideas-negocio` corresponde al identificador funcional `P09`.

## Mapa de bases públicas en esta copia

- `P01` -> `proyectos/p01-inteligencia-comercial-internacional`
- `P02` -> `proyectos/p02-agente-multi-herramienta`
- `P03` -> `proyectos/p03-agente-licitaciones`
- `P04` -> `proyectos/p04-agente-rrhh-candidatos`
- `P05` -> `proyectos/p05-rag-documentacion-interna`
- `P06` -> `proyectos/p06-rag-contratos-legales`
- `P07` -> `proyectos/p07-chatbot-atencion-cliente`
- `P08` -> `proyectos/p08-rag-normativa-comercio`
- `P09` -> `proyectos/p9-evaluador-ideas-negocio`
- `P10` -> `proyectos/p10-dashboard-lenguaje-natural`

## Ejecución local rápida

```bash
# desde la raíz
python -m venv .venv
.venv\Scripts\activate
pip install -r proyectos/p01-inteligencia-comercial-internacional/requirements.txt
```

Cada subproyecto tiene su propio `requirements.txt` y su propio comando `streamlit run`.

## Calidad y CI

Ejecución local de los checks:

```bash
.venv\Scripts\python scripts/ci_lint.py
.venv\Scripts\python scripts/ci_smoke.py
```

Workflow GitHub Actions:

- `.github/workflows/ci.yml`
- Jobs: `lint` y `smoke` con Python 3.11

## Política de repositorio

- No versionar secretos (`.env`) ni artefactos de runtime (`sqlite`, `chroma_db`, `outputs`, `logs`, `site-packages`).
- La raíz usa `.gitignore` global para proteger todo el monorepo.

