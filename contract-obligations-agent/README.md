# contract-obligations-agent

Un agente de revisión contractual auditable, diseñado para apoyar flujos de trabajo empresariales serios.

`contract-obligations-agent` lee contratos, anexos, correos y plantillas internas; extrae obligaciones y fechas; marca riesgos; recupera evidencia trazable; y genera salidas útiles para una primera revisión documental.

No sustituye el asesoramiento jurídico. Está pensado para acelerar la revisión inicial, organizar la evidencia y dejar claro qué está verificado, qué es inferencia y qué sigue necesitando validación humana.

## Qué hace

- Resume un contrato en lenguaje de negocio sin perder base documental.
- Detecta lenguaje de pago, renovación, penalización, confidencialidad, datos y terminación.
- Construye una matriz de obligaciones con responsable, fecha, dependencia, riesgo y explicación.
- Señala vacíos, incoherencias y casos que requieren revisión humana.
- Exporta resultados en JSON, Markdown, CSV y DOCX.

## Qué incluye

- Backend: FastAPI
- Interfaz de demo: Gradio
- Persistencia de demo: SQLite
- Vector store de demo: Chroma local
- Vector store alternativo: adaptador preparado para Qdrant local
- Pasarela LLM: LiteLLM con Groq por defecto
- Modelado: Pydantic
- Pruebas: pytest
- ROI: calculadora editable y transparente

## Flujo principal

`ingest -> parse -> normalize -> classify -> extract -> validate -> summarize -> obligations -> export`

Cada salida conserva trazabilidad a los fragmentos fuente siempre que sea posible.

## Estructura del proyecto

```text
app/                API FastAPI y demo Gradio
core/               Configuración, logging, seguridad, auditoría y base de datos
connectors/         Ingesta de archivos y correo
domain/             Modelos de contrato, cláusulas, obligaciones y riesgo
services/           Parsing, retrieval, vector store, LLM, workflows y exportes
roi/                Supuestos editables y calculadora de ROI
docs/               Arquitectura, ruta a producción y plan de sprints
sample_data/        Fixtures anonimizados de demo y pruebas
tests/              Pruebas unitarias, de integración y end-to-end
scripts/            Lanzador local de la demo
```

## Modos de uso

### Demo

Pensada para ejecución local con coste mínimo:

- SQLite para persistencia
- Chroma para recuperación semántica
- Gradio para la interfaz
- Datos mock anonimizados

### Ruta a producción

La arquitectura ya deja preparadas estas piezas:

- Postgres como backend de persistencia
- Object storage para exportes y adjuntos
- Qdrant como alternativa a Chroma
- Observabilidad más sólida
- Gestión endurecida de secretos y configuración

Más detalle en [docs/production.md](docs/production.md).

## Arranque rápido

Desde la carpeta `contract-obligations-agent`:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts\run_demo.py
```

### API local

```powershell
uvicorn app.main:app --reload
```

### ROI

```powershell
python -m roi.calculator
```

## Qué devuelve

- Resumen ejecutivo: visión corta para negocio.
- Cláusulas detectadas: fragmentos relevantes con evidencia.
- Obligaciones: responsable inferido o vacío, fecha o hito, dependencia, estado y explicación.
- Alertas: severidad, motivo y necesidad de revisión humana.
- Evidencias: fragmentos recuperados con ranking y trazabilidad.
- Exportes: JSON, Markdown, CSV y DOCX.

## Seguridad y criterio

- No realiza acciones destructivas.
- Redacta datos sensibles básicos en modo demo.
- Marca revisión humana cuando el riesgo lo exige.
- Separa extracción objetiva, inferencia razonada y alerta preventiva.
- El sistema es apoyo documental, no un dictamen legal.

## ROI

La carpeta [roi/](roi) contiene una calculadora editable con supuestos transparentes:

- horas de revisión manual por contrato
- volumen mensual de contratos
- coste por hora
- ahorro por extracción inicial
- ahorro por seguimiento de obligaciones
- reducción estimada de omisiones administrativas
- cifras mensuales, anuales y payback

Consulta [roi/README.md](roi/README.md) para ver el detalle.

## Plan de desarrollo

El plan de sprints está documentado en [docs/sprints.md](docs/sprints.md):

- Sprint 0: base del proyecto
- Sprint 1: ingesta y parsing
- Sprint 2: extracción estructurada
- Sprint 3: recuperación y resumen
- Sprint 4: obligaciones y riesgo
- Sprint 5: interfaz y exportes
- Sprint 6: ROI, endurecimiento y pruebas

## Calidad

- Se incluye una suite mínima de pruebas.
- La demo y la API funcionan.
- La estructura está lista para crecer sin rehacer el dominio.

## Datos de ejemplo

La carpeta [sample_data/](sample_data) contiene fixtures anonimizados para demo y pruebas:

- contrato de ejemplo
- correo de renovación
- plantilla de checklist esperada

## Documentación útil

- [Arquitectura](docs/architecture.md)
- [Ruta a producción](docs/production.md)
- [Plan de sprints](docs/sprints.md)
- [ROI](roi/README.md)

## Cierre

El diseño está orientado a pasar de una demo de coste bajo a un producto serio sin cambiar la lógica central. Lo que cambia entre entornos es la infraestructura; el dominio, la trazabilidad y el criterio de revisión permanecen estables.
