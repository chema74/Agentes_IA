# Architecture

## Layers

- `app`: FastAPI and Gradio entrypoints.
- `core`: config, logging, security, audit, database.
- `connectors`: file and email ingestion.
- `domain`: contract, clause, obligation, and risk models.
- `services`: parsing, retrieval, vector store, LLM, workflows, exports.
- `roi`: editable ROI assumptions and calculator.

## Pipeline

`ingest -> parse -> normalize -> classify -> extract -> validate -> summarize -> obligations -> export`

