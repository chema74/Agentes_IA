# Catálogo del Monorepo

Este documento resume el estado actual de `Agentes_IA` como repositorio técnico de agentes de IA (*Artificial Intelligence – Inteligencia Artificial*) aplicada a negocio, documentación, comercio exterior, cumplimiento normativo y automatización empresarial.

El repositorio ya no se presenta como una web pública ni como una landing comercial. Su función principal es actuar como base técnica de portfolio: demos ejecutables, agentes con vocación de producto, utilidades compartidas, validaciones y documentación de apoyo.

---

## Resumen Ejecutivo

`Agentes_IA` está organizado como un monorepo técnico con tres niveles de lectura:

1. Productos estrella.
2. Demos de portfolio.
3. Laboratorio técnico.

La prioridad del repositorio no es acumular ejemplos, sino demostrar capacidad real para construir soluciones de IA aplicables a problemas empresariales concretos.

La lectura recomendada es empezar por los tres productos estrella y usar el resto del repositorio como evidencia técnica complementaria.

---

## Estado General

El repositorio está orientado a:

- Resolver problemas empresariales concretos.
- Separar demos públicas de agentes con estructura de producto.
- Mantener trazabilidad en los resultados generados por IA.
- Documentar límites de uso cuando el dominio sea sensible.
- Priorizar supervisión humana en áreas legales, psicológicas, educativas o de cumplimiento normativo.
- Evitar promesas excesivas sobre autonomía total.
- Facilitar revisión técnica mediante estructura clara, pruebas y scripts de validación.

---

## Estructura Vigente

### `portfolio/`

Contiene demos y prototipos públicos orientados a casos de uso concretos.

Son piezas pensadas para demostrar capacidad técnica, criterio de diseño y aplicabilidad empresarial, sin presentarse necesariamente como productos finales.

### `products/`

Contiene agentes y orquestadores con estructura más cercana a producto.

Incluyen arquitectura más completa, separación de capas, documentación específica, pruebas, configuración y, en algunos casos, rutas de evolución hacia producción.

### `core/`

Contiene utilidades compartidas y piezas reutilizables.

Debe mantenerse estable, ligero y sin efectos secundarios innecesarios al importar configuración o módulos comunes.

### `scripts/`

Contiene checks de CI (*Continuous Integration – Integración Continua*) y utilidades de validación local.

Su función es mantener coherencia estructural, detectar errores básicos y facilitar revisiones repetibles.

### `tests/`

Contiene pruebas mínimas del portfolio y validaciones de estructura.

La cobertura puede ampliarse si algún proyecto pasa de demo a pieza endurecida o producto más serio.

---

## Nivel 1 — Productos Estrella

Estos son los proyectos que deberían aparecer primero en cualquier lectura profesional del portfolio.

---

### 1. Inteligencia Comercial Internacional

Ruta interna:

`portfolio/p01-inteligencia-comercial-internacional`

Nombre comercial recomendado:

**Inteligencia Comercial Internacional con IA**

Qué demuestra:

- Comparación de países y mercados.
- Evaluación orientativa de oportunidades comerciales.
- Análisis asistido por modelo.
- Recuperación de señales externas.
- Ranking orientativo de mercados.
- Uso aplicado de IA en comercio exterior.

Por qué es estratégico:

Este proyecto conecta directamente con negocio, internacionalización, análisis de mercados y toma de decisiones. Es uno de los activos más fuertes del portfolio porque combina IA con criterio económico y comercial.

Estado:

Cerrado. README reescrito con propuesta de valor, descripción del problema que resuelve y enlace al producto equivalente.

Pendiente recomendado:

- Demo final con ejemplo claro de sector, país y resultado (grabación o capturas).

---

### 2. RAG de Documentación Interna

Ruta interna:

`portfolio/p05-rag-documentacion-interna`

Nombre comercial recomendado:

**Asistente de Consulta Documental Interna**

Qué demuestra:

- Carga de documentos PDF (*Portable Document Format – Formato de Documento Portátil*).
- Indexación local de documentación.
- Consulta en lenguaje natural.
- Recuperación de fragmentos relevantes.
- Respuestas con apoyo documental.
- Uso de RAG (*Retrieval-Augmented Generation – Generación Aumentada por Recuperación*).

Por qué es estratégico:

Es una demo muy vendible para empresas. Cualquier PYME (*Small and Medium-sized Enterprise – Pequeña y Mediana Empresa*) con manuales, procedimientos, documentación interna, políticas o guías puede entender rápidamente el valor.

Estado:

Cerrado. Iconos rotos corregidos. Presentable como demo clara.

Pendiente recomendado:

- Reforzar ejemplos de uso empresarial con capturas o casos concretos.

---

### 3. Agente Supervisado de Obligaciones Contractuales

Ruta interna:

`products/contract-obligations-agent`

Nombre comercial recomendado:

**Agente Supervisado de Obligaciones Contractuales**

Qué demuestra:

- Lectura estructurada de contratos y anexos.
- Extracción de obligaciones.
- Identificación de fechas, riesgos y dependencias.
- Evidencias trazables.
- Exportes en JSON (*JavaScript Object Notation – Notación de Objetos JavaScript*), Markdown, CSV (*Comma-Separated Values – Valores Separados por Comas*) y DOCX (*Document Open XML – Documento Open XML*).
- Arquitectura de producto con API (*Application Programming Interface – Interfaz de Programación de Aplicaciones*), demo, persistencia, recuperación semántica y pruebas.

Por qué es estratégico:

Es el proyecto con mayor apariencia de producto real. Muestra arquitectura, dominio, trazabilidad, exportación, criterio de riesgo y posible retorno económico.

Estado:

Cerrado técnicamente como producto base.

Pendiente recomendado:

- Documentar mejor despliegue.
- Añadir límites legales visibles.
- Reforzar conectores reales si se quiere evolucionar a producto utilizable por terceros.
- Mantener siempre la advertencia de revisión humana.

Nota de uso:

No sustituye asesoramiento jurídico. Su función es acelerar una primera revisión documental, ordenar evidencias y señalar posibles puntos de atención.

---

## Nivel 2 — Demos de Portfolio

Estas piezas deben mantenerse como evidencia técnica y comercial complementaria. No todas tienen que tener el mismo peso público.

---

### P02 — Agente Multi-Herramienta

Ruta interna:

`portfolio/p02-agente-multi-herramienta`

Nombre comercial recomendado:

**Copiloto Operativo Multi-Herramienta**

Qué demuestra:

- Orquestación básica de herramientas.
- Coordinación de tareas.
- Uso de agentes para resolver acciones encadenadas.

Estado:

Cerrado. README reescrito explicando el diferencial frente a p05/p06/p07: ilustra el patrón tool calling con decisión autónoma de herramienta, no el patrón RAG.

Pendiente recomendado:

- Nada bloqueante. Revisar si se añade a los proyectos destacados de la web.

---

### P03 — Agente de Licitaciones

Ruta interna:

`portfolio/p03-agente-licitaciones`

Nombre comercial recomendado:

**Asistente de Análisis de Licitaciones**

Qué demuestra:

- Lectura y análisis de oportunidades públicas.
- Extracción de criterios relevantes.
- Apoyo a evaluación inicial de encaje.

Estado:

Cerrado. README reescrito con caso de uso concreto, perfil de usuario objetivo y límites honestos. Diferencia clara respecto a contract-obligations-agent añadida.

Pendiente recomendado:

- Nada bloqueante.

---

### P04 — Agente de Recursos Humanos

Ruta interna:

`portfolio/p04-agente-rrhh-candidatos`

Nombre comercial recomendado:

**Asistente de Preselección de Candidatos**

Qué demuestra:

- Clasificación de perfiles.
- Comparación contra criterios.
- Apoyo a procesos de selección.

Estado:

Cerrado. README reescrito con caso de uso, límites de sesgo, nota de privacidad y advertencia de que la decisión final es siempre del equipo de selección.

Pendiente recomendado:

- Nada bloqueante.

---

### P06 — RAG de Contratos Legales

Ruta interna:

`portfolio/p06-rag-contratos-legales`

Nombre comercial recomendado:

**Consulta Supervisada de Contratos**

Qué demuestra:

- Consulta documental sobre contratos.
- Recuperación de fragmentos relevantes.
- Respuestas asistidas con contexto.

Estado:

Cerrado. Disclaimer añadido en sidebar y subtítulo diferenciando esta demo del producto contract-obligations-agent. Advertencia de revisión humana reforzada.

Pendiente recomendado:

- Nada bloqueante.

---

### P07 — Chatbot de Atención al Cliente

Ruta interna:

`portfolio/p07-chatbot-atencion-cliente`

Nombre comercial recomendado:

**Asistente de Atención al Cliente Supervisado**

Qué demuestra:

- Interacción conversacional básica.
- Respuesta orientada a soporte.
- Posible integración con FAQs (*Frequently Asked Questions – Preguntas Frecuentes*) o bases de conocimiento.

Estado:

Cerrado. Reescrito completamente: bug crítico corregido (page_title decía P08), tema visual alineado con el resto del portfolio (oscuro/dorado), onboarding en 3 pasos añadido, escalado a humano con indicador visual propio.

Pendiente recomendado:

- Nada bloqueante.

---

### P08 — RAG de Normativa de Comercio

Ruta interna:

`portfolio/p08-rag-normativa-comercio`

Nombre comercial recomendado:

**Asistente de Consulta Normativa Comercial**

Qué demuestra:

- Consulta de normativa.
- Recuperación documental.
- Aplicación de RAG a comercio exterior y regulación.

Estado:

Cerrado. page_title e icono corregidos. Aviso de frescura de datos añadido en sidebar y subtítulo. Tag de cabecera coherente con el resto del portfolio.

Pendiente recomendado:

- Incorporar fuentes oficiales versionadas si se endurece a producto.

---

### P09 — Evaluador de Ideas de Negocio

Ruta interna:

`portfolio/p09-evaluador-ideas-negocio`

Nombre comercial recomendado:

**Evaluador Inicial de Ideas de Negocio**

Qué demuestra:

- Análisis estructurado de ideas.
- Evaluación preliminar de viabilidad.
- Priorización orientativa.

Estado:

Cerrado. Encoding roto del prompt interno y de la UI corregido. Iconos rotos en sidebar y estado inicial corregidos. Footer y cabecera alineados con el estilo del portfolio.

Pendiente recomendado:

- Nada bloqueante.

---

### P10 — Dashboard en Lenguaje Natural

Ruta interna:

`portfolio/p10-dashboard-lenguaje-natural`

Nombre comercial recomendado:

**Dashboard Consultable en Lenguaje Natural**

Qué demuestra:

- Consulta de datos mediante lenguaje natural.
- Visualización orientada a negocio.
- Interacción más accesible con información tabular.

Estado:

Cerrado. page_title e icono corregidos. Caracter unicode roto en estado inicial corregido.

Pendiente recomendado:

- Endurecer sandbox si pasa a multiusuario.

---

## Nivel 3 — Laboratorio Técnico

Esta sección agrupa proyectos avanzados, sensibles o experimentales. No deberían venderse todos al mismo nivel que los productos estrella.

Su valor principal es demostrar capacidad de arquitectura, exploración de dominios complejos y diseño de agentes especializados.

---

### Logística Autónoma Supervisada

Ruta interna:

`products/a2a-self-healing-logistics-agent`

Nombre técnico original:

`a2a-self-healing-logistics-agent`

Qué demuestra:

- Agentes aplicados a logística.
- Supervisión de incidencias.
- Posible recuperación ante fallos operativos.

Estado:

Cerrado técnicamente.

Cautela:

Requiere operación, runbook y validación con datos reales antes de presentarlo como solución productiva.

---

### Agente de Cumplimiento de Políticas

Ruta interna:

`products/apollo-policy-enforcer-agent`

Nombre técnico original:

`apollo-policy-enforcer-agent`

Qué demuestra:

- Evaluación de políticas.
- Control de cumplimiento.
- Posible enforcement supervisado.

Estado:

Cerrado técnicamente.

Cautela:

Requiere validación estricta de permisos, alcance y consecuencias antes de cualquier uso real.

---

### Inteligencia Geopolítica Comercial

Ruta interna:

`products/geopolitical-trade-intelligence-agent`

Nombre técnico original:

`geopolitical-trade-intelligence-agent`

Qué demuestra:

- Análisis de riesgo geopolítico.
- Aplicación a comercio internacional.
- Cruce entre señales externas, negocio y decisión estratégica.

Estado:

Cerrado.

Cautela:

Dominio sensible por frescura de datos, interpretación de riesgo y dependencia de fuentes externas.

---

### Asistente Legal Supervisado

Ruta interna:

`products/autonomous-legal-counsel-agent`

Nombre técnico original:

`autonomous-legal-counsel-agent`

Nombre comercial recomendado:

**Asistente Legal Supervisado**

Qué demuestra:

- Exploración de flujos legales asistidos.
- Organización de argumentos y documentación.
- Apoyo preliminar en análisis legal.

Estado:

Cerrado.

Cautela:

Dominio legal sensible. No debe presentarse como abogado autónomo ni como sustituto de asesoramiento jurídico profesional.

---

### Orquestador Psicoeducativo Supervisado

Ruta interna:

`products/nspa-psychological-orchestrator`

Nombre técnico original:

`nspa-psychological-orchestrator`

Nombre comercial recomendado:

**Orquestador Psicoeducativo Supervisado**

Qué demuestra:

- Orquestación de flujos conversacionales sensibles.
- Estructura de apoyo, derivación y límites.
- Diseño de agentes con cautela de dominio.

Estado:

Cerrado técnicamente.

Cautela:

Dominio psicológico sensible. No debe presentarse como diagnóstico, terapia ni sustituto de profesionales sanitarios.

---

### Agente de Evidencias de Cumplimiento Normativo

Ruta interna:

`products/audit-compliance-evidence-agent`

Nombre técnico original:

`audit-compliance-evidence-agent`

Qué demuestra:

- Organización de evidencias.
- Apoyo a auditoría.
- Trazabilidad documental.
- Preparación de documentación de cumplimiento.

Estado:

Cerrado.

Cautela:

Requiere despliegue, UX (*User Experience – Experiencia de Usuario*) final y validación con procesos reales.

---

### Orquestador de Integridad Educativa

Ruta interna:

`products/agentic-learning-integrity-orchestrator`

Nombre técnico original:

`agentic-learning-integrity-orchestrator`

Qué demuestra:

- Supervisión de procesos educativos asistidos por IA.
- Integridad académica.
- Diseño de flujos de revisión.

Estado:

Cerrado técnicamente.

Cautela:

Contexto educativo sensible. Debe evitar decisiones automáticas injustificadas sobre estudiantes o docentes.

---

### Orquestador de Cambio Organizacional

Ruta interna:

`products/change-process-coaching-orchestrator`

Nombre técnico original:

`change-process-coaching-orchestrator`

Qué demuestra:

- Apoyo a procesos de cambio.
- Coaching organizacional supervisado.
- Diseño de flujos de acompañamiento.

Estado:

Cerrado técnicamente.

Cautela:

Dominio organizacional sensible. Debe presentarse como apoyo metodológico, no como sustituto del criterio directivo o humano.

---

## Lectura Recomendada del Repositorio

Para una revisión profesional, se recomienda este orden:

1. Revisar primero el `README.md` principal.
2. Revisar este `CATALOGO.md`.
3. Entrar en los tres productos estrella:
   - `portfolio/p01-inteligencia-comercial-internacional`
   - `portfolio/p05-rag-documentacion-interna`
   - `products/contract-obligations-agent`
4. Revisar después las demos de portfolio según el caso de uso.
5. Usar el laboratorio técnico como evidencia de amplitud, arquitectura y exploración avanzada.

---

## Estado Global — Mayo 2026

El portfolio está cerrado y presentable. Todos los proyectos han sido revisados, los bugs corregidos y la documentación actualizada.

### Completado en esta sesión

- README de p01, p02, p03 y p04 reescritos con propuesta de valor clara.
- p07 reescrito completamente: bug P08→P07 corregido, tema visual alineado, onboarding añadido.
- p05, p08, p09 y p10: iconos y encoding rotos corregidos, page_title e icono consistentes.
- p06: disclaimer de diferenciación respecto al producto legal serio añadido.
- Web pública (contacto.html): email, LinkedIn, GitHub y Formspree configurados con datos reales.

### Pendiente menor (no bloquea el portfolio)

- Grabación o capturas de demo para p01 (el proyecto estrella merece un ejemplo visual).
- Runbooks de despliegue para los productos si se van a publicar como entregables operativos.
- Endurecer sandbox de p10 si pasa a multiusuario.

### Reglas de mantenimiento

- Mantener `.env.example` sin secretos reales en todos los proyectos.
- Evitar artefactos locales (bases vectoriales, cachés, exportes) dentro del repositorio.
- Ampliar pruebas solo en proyectos que pasen de demo a producto endurecido.
- Confirmar rotación de claves antes de cualquier publicación pública (ver `SECURITY_ROTATION.md`).

---

## Criterio de Presentación Pública

No todos los proyectos deben tener la misma visibilidad.

### Mostrar primero

- Inteligencia Comercial Internacional con IA.
- Asistente de Consulta Documental Interna.
- Agente Supervisado de Obligaciones Contractuales.

### Mostrar como demos complementarias

- Licitaciones.
- Recursos Humanos.
- Contratos.
- Normativa de comercio.
- Dashboard en lenguaje natural.
- Evaluador de ideas.
- Atención al cliente.
- Copiloto multi-herramienta.

### Mantener como laboratorio técnico

- Agentes legales sensibles.
- Orquestadores psicológicos o educativos.
- Agentes de enforcement.
- Proyectos con dependencia fuerte de operación, permisos o datos frescos.

---

## Cierre

Este monorepo debe leerse como una base técnica de IA aplicada, no como una colección dispersa de experimentos.

Su valor está en demostrar que se pueden construir agentes útiles con estructura, límites, trazabilidad y orientación empresarial.

La evolución natural del repositorio debería centrarse en menos proyectos visibles, mejor explicados y con mayor claridad comercial.

---

## 🪪 Licencia y Autoría

Publicado bajo licencia Creative Commons CC BY-SA 4.0 International.  
© 2026 – José María Tinajero Ríos. Todos los derechos compartidos.