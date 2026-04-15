# Arquitectura

## Principios

- arquitectura limpia
- dominio desacoplado de infraestructura
- trazabilidad total
- decision sensible siempre revisable por humano
- coste bajo en demo, evolucion limpia a produccion

## Capas

### `app`
Expone dos entradas:
- API JSON para integraciones y automatizacion controlada
- web ligera para compliance, auditor y owner

### `core`
Contiene configuracion, logging, auth, auditoria, seguridad y persistencia base.

### `connectors`
Resuelven la entrada y salida de artefactos sin contaminar el dominio.

### `domain`
Modela `AUDIT_SCOPE`, `CONTROL`, `EVIDENCE`, `FINDING`, `REMEDIATION`, `AUDIT_PACKAGE` y sus relaciones.

### `services`
Orquesta parsing, mapping, evaluacion, exportes y workflow completo.

## Pipeline

`control catalog -> evidence ingest -> normalize -> map evidence to controls -> evaluate coverage -> detect gaps -> generate findings -> review -> export audit package`

## Reglas de gobierno implementadas

- un control sin owner genera gap
- evidencia insuficiente no puede marcar cobertura completa
- controles criticos y hallazgos altos/criticos fuerzan revision humana
- los exports describen apoyo al proceso, no certificacion formal
- cada alta, mapping, revision, evaluacion y export genera evento auditable

## Persistencia demo vs produccion

- demo: store en memoria para operativa rapida y SQL base documentado
- produccion: Postgres/Supabase + storage real sin redisenar el dominio

## Retrieval

La version base usa reglas y busqueda lexical ligera. `pgvector` queda preparado por configuracion para escenarios donde compense ampliar recuperacion semantica.
