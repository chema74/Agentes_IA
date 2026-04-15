# Ruta a producción

## Modo demo

- SQLite para la persistencia local.
- Chroma para la recuperación local.
- Sistema de archivos local para exportes y datos de ejemplo.
- Gradio como interfaz principal para la demo.
- Groq como pasarela LLM por defecto a través de LiteLLM.

## Ruta lista para producción

- Sustituir SQLite por Postgres usando los mismos modelos de dominio.
- Sustituir el almacenamiento local de exportes por object storage.
- Mantener intacta la capa de workflows.
- Cambiar Chroma por Qdrant sin alterar las reglas de negocio.
- Colocar FastAPI detrás de un servicio interno si hace falta.
- Añadir logging estructurado, trazas, métricas y gestión de secretos.

## Lo que permanece estable

- Los modelos de dominio.
- La orquestación de workflows.
- La trazabilidad de evidencias.
- Las reglas de riesgo y revisión.
- Los contratos de exportación.

## Lo primero que cambia

- El backend de base de datos.
- El almacenamiento de artefactos.
- La observabilidad.
- La gestión de secretos.
- La topología de despliegue.
