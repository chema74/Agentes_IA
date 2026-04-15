# Plan de sprints

Sprint 0 - Base del proyecto y setup
- Crear la estructura de carpetas.
- Configurar FastAPI, Gradio, SQLite, Chroma local y LiteLLM.
- Preparar la configuracion por entorno: demo y produccion.
- Anadir logging estructurado, manejo de errores y `.env.example`.

Sprint 1 - Ingesta y parsing documental
- Implementar carga de PDF, DOCX y EML.
- Normalizar texto y metadatos.
- Anadir validaciones de entrada.
- Crear archivos de ejemplo y documentos ficticios anonimizados.

Sprint 2 - Extraccion estructurada y dominio legal-operativo
- Definir esquemas Pydantic para clausulas, obligaciones, fechas, alertas y dependencias.
- Implementar extraccion inicial de clausulas y obligaciones.
- Detectar vencimientos, renovaciones y penalizaciones.
- Crear reglas base de validacion.

Sprint 3 - Recuperacion con evidencia y resumen ejecutivo
- Implementar indexacion en Chroma.
- Construir recuperacion con fragmentos citables.
- Generar un resumen ejecutivo con trazabilidad.
- Anadir comparacion contra checklist o plantilla contractual.

Sprint 4 - Matriz de obligaciones y riesgo
- Construir la matriz de obligaciones.
- Clasificar alertas por severidad.
- Marcar los casos de riesgo alto para revision humana obligatoria.
- Anadir explicacion de por que se marca cada riesgo.

Sprint 5 - Interfaz demo y exportaciones
- Completar la interfaz Gradio.
- Anadir vistas de resumen, clausulas, obligaciones y alertas.
- Implementar exportacion a JSON, Markdown, CSV y DOCX.
- Validar el flujo de extremo a extremo.

Sprint 6 - ROI, endurecimiento y pruebas
- Implementar el modulo ROI editable.
- Anadir pruebas unitarias e integracion.
- Endurecer validaciones, auditoria y redaccion opcional de datos sensibles.
- Documentar la evolucion a Postgres y object storage para produccion.
