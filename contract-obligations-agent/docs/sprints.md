# Sprint plan

Sprint 0 — Base del proyecto y setup
- Crear estructura de carpetas
- Configurar FastAPI, Gradio, SQLite, Chroma local y LiteLLM
- Preparar configuración por entorno: demo y production
- Añadir logging estructurado, manejo de errores y `.env.example`

Sprint 1 — Ingesta y parsing documental
- Implementar carga de PDF, DOCX y EML
- Normalizar texto y metadatos
- Añadir validaciones de entrada
- Crear fixtures y documentos mock anonimizados

Sprint 2 — Extracción estructurada y dominio legal-operativo
- Definir esquemas Pydantic para cláusulas, obligaciones, fechas, alertas y dependencias
- Implementar extracción inicial de cláusulas y obligaciones
- Detectar vencimientos, renovaciones y penalizaciones
- Crear reglas base de validación

Sprint 3 — Retrieval con evidencia y resumen ejecutivo
- Implementar indexación en Chroma
- Construir retrieval con fragmentos citables
- Generar resumen ejecutivo con trazabilidad
- Añadir comparación contra checklist o plantilla contractual

Sprint 4 — Matriz de obligaciones y riesgo
- Construir matriz de obligaciones
- Clasificar alertas por severidad
- Marcar casos de riesgo alto para revisión humana obligatoria
- Añadir explicación de por qué se marcó cada riesgo

Sprint 5 — UI demo y exportaciones
- Completar interfaz Gradio
- Añadir vistas de resumen, cláusulas, obligaciones y alertas
- Implementar exportación a JSON, Markdown, CSV y DOCX
- Validar flujo end-to-end

Sprint 6 — ROI, hardening y tests
- Implementar módulo ROI editable
- Añadir tests unitarios e integración
- Endurecer validaciones, auditoría y redacción opcional de datos sensibles
- Documentar evolución a Postgres y object storage para producción

