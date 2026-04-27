# Arquitectura

## Capas

- `app`: puntos de entrada de FastAPI y Gradio.
- `core`: configuración, logging, seguridad, auditoría y base de datos.
- `connectors`: ingesta de archivos y correo.
- `domain`: modelos de contrato, cláusulas, obligaciones y riesgo.
- `services`: parsing, recuperación, vector store, LLM, workflows y exportes.
- `roi`: supuestos editables y calculadora de ROI.

## Evolución a producción

- SQLite puede sustituirse por Postgres sin tocar la capa de dominio.
- Chroma local puede sustituirse por Qdrant sin cambiar la capa de workflows.
- Las rutas locales de exportación pueden moverse a object storage.
- Los secretos, la observabilidad y la topología de despliegue quedan fuera del dominio central.

## Pipeline

`ingest -> parse -> normalize -> classify -> extract -> validate -> summarize -> obligations -> export`
