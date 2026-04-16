# A2A Self-Healing Logistics Agent

Agente API-first para continuidad logistica. Detecta disrupciones, descubre peers A2A, negocia capacidad alternativa, evalua riesgo de SLA y ejecuta recuperaciones bajo governance-as-code.

## Stack

- Python 3.11
- FastAPI
- LangGraph
- Supabase
- Upstash Redis
- Neon
- A2A + MCP
- Groq con Llama 8B

## API

- `GET /api/health`
- `POST /api/disruptions/evaluate`
- `POST /api/recovery/execute`
- `GET /api/tasks/{task_id}`
- `GET /api/recovery-plans/{plan_id}`
- `GET /api/audit/{reference}`
