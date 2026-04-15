# Sprint plan

Sprint 0 — Base del proyecto y setup
- Crear estructura de carpetas
- Configurar FastAPI, Gradio, SQLite, Chroma local y LiteLLM
- Preparar configuracion por entorno: demo y production
- Anadir logging estructurado, manejo de errores y `.env.example`

Sprint 1 — Ingesta y parsing documental
- Implementar carga de PDF, DOCX y EML
- Normalizar texto y metadatos
- Anadir validaciones de entrada
- Crear fixtures y documentos mock anonimizados

Sprint 2 — Extraccion estructurada y dominio legal-operativo
- Definir esquemas Pydantic para clausulas, obligaciones, fechas, alertas y dependencias
- Implementar extraccion inicial de clausulas y obligaciones
- Detectar vencimientos, renovaciones y penalizaciones
- Crear reglas base de validacion

Sprint 3 — Retrieval con evidencia y resumen ejecutivo
- Implementar indexacion en Chroma
- Construir retrieval con fragmentos citables
- Generar resumen ejecutivo con trazabilidad
- Anadir comparacion contra checklist o plantilla contractual

Sprint 4 — Matriz de obligaciones y riesgo
- Construir matriz de obligaciones
- Clasificar alertas por severidad
- Marcar casos de riesgo alto para revision humana obligatoria
- Anadir explicacion de por que se marco cada riesgo

Sprint 5 — UI demo y exportaciones
- Completar interfaz Gradio
- Anadir vistas de resumen, clausulas, obligaciones y alertas
- Implementar exportacion a JSON, Markdown, CSV y DOCX
- Validar flujo end-to-end

Sprint 6 — ROI, hardening y tests
- Implementar modulo ROI editable
- Anadir tests unitarios e integracion
- Endurecer validaciones, auditoria y redaccion opcional de datos sensibles
- Documentar evolucion a Postgres y object storage para produccion
