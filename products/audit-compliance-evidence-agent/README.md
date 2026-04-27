# audit-compliance-evidence-agent

Sistema de auditoria operativa y compliance orientado a controles, evidencias, hallazgos y remediaciones con trazabilidad completa.

No es un simple gestor documental. No es un chat con archivos. Es una base seria para preparar auditorias internas, organizar evidencias, detectar huecos y generar paquetes auditables reutilizables.

## Propuesta de valor

- reduce trabajo manual de preparacion de auditoria
- conecta controles con evidencias trazables
- separa evidencia real, inferencia, gap y hallazgo
- no afirma cumplimiento absoluto sin revision humana
- no cierra hallazgos criticos automaticamente
- deja un camino claro de demo a produccion sin rehacer el dominio

## Capacidades principales

- catalogo de controles configurable
- ingesta de evidencias PDF, DOCX, TXT, CSV, logs, tickets e imagenes como referencia
- normalizacion y clasificacion de evidencias
- mapping control-evidencia asistido con confianza y justificacion
- evaluacion de cobertura por control
- deteccion de gaps operativos y documentales
- generacion de hallazgos explicables
- seguimiento de remediaciones
- exportacion de paquete de auditoria en ZIP con manifiestos
- trazabilidad completa de eventos relevantes

## Stack

- Python 3.11
- FastAPI
- Jinja2 + HTMX
- Supabase como destino natural de Postgres, Auth y Storage
- LiteLLM con Groq por defecto
- soporte preparado para OpenAI, Gemini y Anthropic
- Pydantic
- SQLAlchemy
- pytest

## Arquitectura

El sistema se organiza por capas:

- `app/`: API JSON y web ligera
- `core/`: configuracion, seguridad, logging, auth, auditoria y base de datos
- `connectors/`: archivos, logs, tickets y storage
- `domain/`: modelo principal de negocio
- `services/`: parsing, mapping, evaluacion, exports, retrieval y workflows
- `sample_data/`: dataset demo anonimo
- `docs/`: arquitectura y modelo operativo
- `roi/`: calculadora editable de ROI

## Flujo principal

`control catalog -> evidence ingest -> normalize -> map evidence to controls -> evaluate coverage -> detect gaps -> generate findings -> review -> export audit package`

## Arranque local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts\bootstrap_demo.py
python scripts\run_dev.py
```

Abrir despues `http://127.0.0.1:8000`.

## Usuarios demo

- `compliance@example.com` / `demo`
- `auditor@example.com` / `demo`
- `owner@example.com` / `demo`

## API principal

- `GET /api/health`
- `POST /api/auth/login`
- `GET/POST /api/scopes`
- `GET/POST /api/controls`
- `POST /api/controls/import`
- `GET /api/evidence`
- `POST /api/evidence/upload`
- `GET /api/mappings`
- `POST /api/mappings/suggest/{scope_id}`
- `POST /api/mappings/review/{mapping_id}`
- `POST /api/evaluations/run/{scope_id}`
- `GET /api/findings`
- `POST /api/findings/review/{finding_id}`
- `GET/POST /api/remediations`
- `GET /api/packages`
- `POST /api/packages/export/{scope_id}`

## Documentacion

- [Arquitectura](docs/architecture.md)
- [Demo vs produccion](docs/demo-vs-production.md)
- [Modelo de controles](docs/control-model.md)
- [Modelo de evidencias](docs/evidence-model.md)
- [Modelo de hallazgos](docs/findings-model.md)
- [Plan de sprints](docs/sprints.md)
- [ROI](roi/README.md)

## Limites del sistema

- No certifica cumplimiento.
- No sustituye la revision de auditoria.
- No inventa evidencias ni relaciones no verificables.
- Los hallazgos altos y criticos requieren validacion humana.
- La demo usa almacenamiento local como sustituto pragmatico de Supabase Storage para no bloquear desarrollo offline.

## Evolucion a produccion

El dominio no depende de una demo local. La transicion natural es:

- sustituir el storage local por buckets reales de Supabase
- usar Postgres real y auth de Supabase en lugar de datos demo
- endurecer secretos, sesiones y politicas de acceso
- conectar fuentes reales de tickets, logs y evidencias sin tocar la capa de dominio
