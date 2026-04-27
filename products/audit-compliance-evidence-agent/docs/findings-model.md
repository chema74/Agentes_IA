# Modelo de hallazgos

Un hallazgo es una observacion explicable derivada de gaps detectados durante la evaluacion de cobertura.

## Campos base

- `id`
- `scope_id`
- `control_id`
- `title`
- `severity`
- `explanation`
- `confidence`
- `preliminary_recommendation`
- `human_review_required`
- `status`

## Severidades

- `low`
- `medium`
- `high`
- `critical`

## Reglas

- hallazgos `high` y `critical` requieren validacion humana
- el sistema puede proponer recomendacion preliminar, pero no cerrar el hallazgo critico automaticamente
- cada hallazgo puede enlazar varias evidencias relacionadas para justificar su trazabilidad
