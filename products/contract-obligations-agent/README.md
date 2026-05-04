# contract-obligations-agent

Un agente de revision contractual auditable, disenado para apoyar flujos de trabajo empresariales serios.

`contract-obligations-agent` lee contratos, anexos, correos y plantillas internas; extrae obligaciones y fechas; marca riesgos; recupera evidencia trazable; y genera salidas utiles para una primera revision documental.

No sustituye el asesoramiento juridico. Esta pensado para acelerar la revision inicial, organizar la evidencia y dejar claro que esta verificado, que es inferencia y que sigue necesitando validacion humana.

## Que hace

- Resume un contrato en lenguaje de negocio sin perder base documental.
- Detecta lenguaje de pago, renovacion, penalizacion, confidencialidad, datos y terminacion.
- Construye una matriz de obligaciones con responsable, fecha, dependencia, riesgo y explicacion.
- Senala vacios, incoherencias y casos que requieren revision humana.
- Exporta resultados en JSON, Markdown, CSV y DOCX.

## Que incluye

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
core/               Configuracion, logging, seguridad, auditoria y base de datos
connectors/         Ingesta de archivos y correo
domain/             Modelos de contrato, clausulas, obligaciones y riesgo
services/           Parsing, retrieval, vector store, LLM, workflows y exportes
roi/                Supuestos editables y calculadora de ROI
docs/               Arquitectura, ruta a produccion y plan de sprints
sample_data/        Fixtures anonimizados de demo y pruebas
tests/              Pruebas unitarias, de integracion y end-to-end
scripts/            Lanzador local de la demo
```

## Modos de uso

### Demo

Pensada para ejecucion local con coste minimo:

- SQLite para persistencia
- Chroma para recuperacion semantica
- Gradio para la interfaz
- Datos ficticios anonimizados

### Ruta a produccion

La arquitectura ya deja preparadas estas piezas:

- Postgres como backend de persistencia
- Object storage para exportes y adjuntos
- Qdrant como alternativa a Chroma
- Observabilidad mas solida
- Gestion endurecida de secretos y configuracion

Mas detalle en [docs/production.md](docs/production.md).

## Arranque rapido

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

## Que devuelve

- Resumen ejecutivo: vision corta para negocio.
- Clausulas detectadas: fragmentos relevantes con evidencia.
- Obligaciones: responsable inferido o vacio, fecha o hito, dependencia, estado y explicacion.
- Alertas: severidad, motivo y necesidad de revision humana.
- Evidencias: fragmentos recuperados con ranking y trazabilidad.
- Exportes: JSON, Markdown, CSV y DOCX.

## Seguridad y criterio

- No realiza acciones destructivas.
- Redacta datos sensibles basicos en modo demo.
- Marca revision humana cuando el riesgo lo exige.
- Separa extraccion objetiva, inferencia razonada y alerta preventiva.
- El sistema es apoyo documental, no un dictamen legal.

## ROI

La carpeta [roi/](roi) contiene una calculadora editable con supuestos transparentes:

- horas de revision manual por contrato
- volumen mensual de contratos
- coste por hora
- ahorro por extraccion inicial
- ahorro por seguimiento de obligaciones
- reduccion estimada de omisiones administrativas
- cifras mensuales, anuales y periodo de recuperacion

Consulta [roi/README.md](roi/README.md) para ver el detalle.

## Plan de desarrollo

El plan de sprints esta documentado en [docs/sprints.md](docs/sprints.md):

- Sprint 0: base del proyecto
- Sprint 1: ingesta y parsing
- Sprint 2: extraccion estructurada
- Sprint 3: recuperacion y resumen
- Sprint 4: obligaciones y riesgo
- Sprint 5: interfaz y exportes
- Sprint 6: ROI, endurecimiento y pruebas

## Calidad

- Se incluye una suite minima de pruebas.
- La demo y la API funcionan.
- La estructura esta lista para crecer sin rehacer el dominio.

## Datos de ejemplo

La carpeta [sample_data/](sample_data) contiene archivos de ejemplo anonimizados para demo y pruebas:

- contrato de ejemplo
- correo de renovacion
- plantilla de checklist esperada

## Documentacion util

- [Arquitectura](docs/architecture.md)
- [Ruta a produccion](docs/production.md)
- [Plan de sprints](docs/sprints.md)
- [ROI](roi/README.md)

## Cierre

El diseno esta orientado a pasar de una demo de coste bajo a un producto serio sin cambiar la logica central. Lo que cambia entre entornos es la infraestructura; el dominio, la trazabilidad y el criterio de revision permanecen estables.
