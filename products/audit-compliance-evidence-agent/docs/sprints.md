# Sprints

Sprint 0 — Foundation and governance setup
- Crear estructura completa del repositorio
- Configurar FastAPI, Supabase, Auth, Storage y base de datos
- Preparar `.env.example`, logging estructurado, configuracion por entorno y usuarios mock
- Crear dataset mock de controles, evidencias y hallazgos

Sprint 1 — Control catalog y modelo de dominio
- Modelar CONTROL, EVIDENCE, FINDING, REMEDIATION, AUDIT_PACKAGE y AUDIT_SCOPE
- Implementar catalogo de controles configurable
- Anadir validaciones de integridad
- Preparar estados base de control y evidencia

Sprint 2 — Evidence ingest y normalizacion
- Implementar ingesta de PDF, DOCX, TXT, CSV y artefactos simples
- Extraer metadatos basicos
- Clasificar tipo de evidencia
- Detectar contenido insuficiente o problematico
- Persistir evidencias y artefactos

Sprint 3 — Mapping y coverage evaluation
- Implementar mapping control-evidencia
- Permitir mapping asistido y revision manual
- Registrar confianza y justificacion
- Evaluar cobertura por control
- Detectar controles no cubiertos o parcialmente cubiertos

Sprint 4 — Gaps, hallazgos y remediaciones
- Detectar gaps
- Generar hallazgos explicables
- Asociar hallazgos a controles y evidencias
- Registrar remediaciones propuestas y estado
- Anadir severidad y necesidad de validacion humana

Sprint 5 — UI web, exportacion y ROI
- Construir interfaz ligera con Jinja2 + HTMX
- Mostrar controles, evidencias, hallazgos, gaps y remediaciones
- Implementar exportacion del paquete de auditoria
- Crear modulo ROI editable
- Anadir metricas basicas de uso y ahorro

Sprint 6 — Hardening, tests y ruta a produccion
- Anadir tests unitarios, integracion y e2e
- Endurecer seguridad y trazabilidad
- Documentar diferencia demo/produccion
- Validar flujo end-to-end con varios escenarios
- Dejar preparado el paso a fuentes reales sin tocar dominio
