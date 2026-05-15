# Portfolio IA Aplicada

Monorepo tecnico de agentes de IA aplicada a negocio, documentacion, comercio exterior, cumplimiento normativo y automatizacion empresarial.

Este repositorio es una base tecnica de portfolio: demos ejecutables, productos con vocacion de uso real, utilidades compartidas, validaciones y documentacion de apoyo.

## Enfoque

- Resolver problemas empresariales concretos.
- Priorizar trazabilidad, limites claros y supervision humana en dominios sensibles.
- Separar demos de portfolio de agentes con estructura de producto.
- Mantener una base simple de ejecutar, revisar y evolucionar.

## Mapa rapido

- `core/`: utilidades compartidas.
- `portfolio/`: demos y prototipos publicos.
- `products/`: agentes con estructura de producto.
- `scripts/`: validaciones de CI y checks locales.
- `tests/`: pruebas de estructura y regresion minima.

## Proyectos destacados

- `portfolio/p01-inteligencia-comercial-internacional`
- `portfolio/p05-rag-documentacion-interna`
- `products/agente-obligaciones-contractuales`

Estado global por proyecto en [CATALOGO.md](CATALOGO.md).

## Estado actual

- El codigo principal vive en `portfolio/` y `products/`.
- CI valida estructura, compilacion Python, tests minimos y tests por producto.
- `portfolio/` es la ruta canonica para demos; `proyectos/` queda retirado.

## Checks locales

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe scripts/ci_quality.py
.venv\Scripts\python.exe scripts/ci_release_guard.py
.venv\Scripts\python.exe scripts/ci_lint.py
.venv\Scripts\python.exe scripts/ci_smoke.py
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts/ci_products.py
.venv\Scripts\python.exe scripts/ci_monorepo_tests.py
```

Nota: evita `pytest` plano en la raiz para todo `products/` y `portfolio/`; usa `scripts/ci_monorepo_tests.py` para aislamiento por carpeta.

## Operacion y release

- Runbook operativo: [docs/OPERATIONS.md](docs/OPERATIONS.md)
- Politica de release: [docs/RELEASE.md](docs/RELEASE.md)
- Changelog: [.github/workflows/release-drafter.yml](.github/workflows/release-drafter.yml)
- Endurecimiento de cobertura: [.github/workflows/quality-ratchet.yml](.github/workflows/quality-ratchet.yml)

## Politica del repositorio

- No versionar secretos (`.env`) ni artefactos de runtime.
- No versionar entornos virtuales, caches ni exportes locales.
- Mantener `README.md`, `requirements.txt` y entrypoint por proyecto.
- Documentar limites de uso en dominios sensibles.

## Licencia y autoria

Publicado bajo licencia Creative Commons CC BY-SA 4.0 International.

(c) 2026 - Jose Maria Tinajero Rios.
