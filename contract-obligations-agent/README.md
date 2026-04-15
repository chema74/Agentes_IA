# contract-obligations-agent

Contract review and obligation tracking agent with auditable evidence.

## Modes

- Demo: SQLite + local Chroma + Gradio.
- Production: prepared for Postgres, object storage, observability, and hardened secrets.

## Run demo

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r contract-obligations-agent/requirements.txt
copy contract-obligations-agent\.env.example contract-obligations-agent\.env
python contract-obligations-agent\scripts\run_demo.py
```

## Safety

- Not legal advice.
- Human review required for high-risk cases.
- Every output must carry evidence.

