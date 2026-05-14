# Operacion del Monorepo

## Objetivo

Definir un estandar operativo comun para `portfolio/` y `products/` con trazabilidad, calidad continua y recuperacion predecible.

## SLOs Minimos

- Disponibilidad de CI: >= 99% mensual.
- Tiempo medio de recuperacion de pipeline rojo (MTTR): <= 24h.
- Tasa de exito de tests en `main`: >= 98% semanal.
- Tiempo maximo de cierre de hallazgo critico de seguridad: <= 72h.

## Señales Operativas

- Estado de jobs en GitHub Actions (`quality`, `release-metadata`, `lint`, `smoke`, `portfolio-tests`, `products-tests`).
- Artefacto `coverage.xml` por ejecucion para auditoria de cobertura.
- Tendencia de `skipped tests` en productos para evitar deuda invisible.

## Protocolo de Incidente

1. Identificar job roto y commit exacto.
2. Reproducir localmente con el script equivalente de CI.
3. Aplicar fix minimo y abrir PR con evidencia de ejecucion.
4. Marcar causa raiz y accion preventiva en descripcion del PR.

## Cadencia de Hardening

- Semanal: revisar warnings de seguridad y debt de `skipped`.
- Quincenal: actualizar `requirements-dev.txt` y validar compatibilidad.
- Mensual: revisar umbral de cobertura y elevarlo si el repositorio crece.
