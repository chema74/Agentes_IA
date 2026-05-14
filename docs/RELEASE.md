# Release y Versionado

## Regla de version

Cada producto en `products/*` debe declarar en `pyproject.toml`:

- `project.name`
- `project.version` en formato SemVer estricto: `X.Y.Z`

El job `release-metadata` bloquea merges si falta o es invalido.

## Politica de cambios

- `MAJOR`: ruptura de contrato de API o flujo principal.
- `MINOR`: funcionalidad nueva compatible.
- `PATCH`: correcciones sin ruptura.

## Checklist de release

1. `quality` en verde (ruff, mypy, bandit, cobertura minima).
2. `portfolio-tests` y `products-tests` en verde.
3. Version actualizada en productos afectados.
4. Riesgos y limites operativos documentados en README o docs del producto.
5. Rollback definido (commit/tag anterior estable).

## Evidencia minima por release

- Link a workflow exitoso.
- Lista de productos/versiones impactadas.
- Resumen de riesgos residuales aceptados.
