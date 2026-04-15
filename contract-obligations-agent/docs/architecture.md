# Architecture

## Layers

- `app`: FastAPI and Gradio entrypoints.
- `core`: config, logging, security, audit, database.
- `connectors`: file and email ingestion.
- `domain`: contract, clause, obligation, and risk models.
- `services`: parsing, retrieval, vector store, LLM, workflows, exports.
- `roi`: editable ROI assumptions and calculator.

## Production evolution

- SQLite can be replaced by Postgres without changing the domain layer.
- Local Chroma can be replaced by Qdrant without changing the workflow layer.
- Local export paths can be swapped for object storage.
- Secrets, observability, and deployment topology stay outside the core domain.

## Pipeline

`ingest -> parse -> normalize -> classify -> extract -> validate -> summarize -> obligations -> export`
