# Demo to Production

## Demo mode

- SQLite for local persistence.
- Chroma for local retrieval.
- Local filesystem for exports and sample data.
- Gradio for the main operator demo.
- Groq as the default LLM gateway through LiteLLM.

## Production-ready path

- Replace SQLite with Postgres using the same domain models.
- Replace local export storage with object storage.
- Keep the workflow layer unchanged.
- Swap Chroma for Qdrant without changing business rules.
- Move FastAPI behind an internal service boundary if needed.
- Add structured logging, tracing, metrics, and secrets management.

## What stays stable

- Domain models.
- Workflow orchestration.
- Evidence traceability.
- Risk and review rules.
- Export contracts.

## What changes first

- Database backend.
- Artifact storage.
- Observability.
- Secret management.
- Deployment topology.
