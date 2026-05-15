# Catalogo del Monorepo

Este documento resume el estado de `Agentes_IA` como monorepo tecnico de agentes de IA aplicada.

## Resumen ejecutivo

`Agentes_IA` se organiza en tres niveles:

1. Productos con vocacion operativa (`products/`).
2. Demos de portfolio (`portfolio/`).
3. Utilidades y validaciones (`core/`, `scripts/`, `tests/`).

La prioridad es demostrar capacidad real para construir soluciones aplicables a negocio, con trazabilidad y limites de uso.

## Estado general

- Estructura de monorepo clara y consistente.
- Cobertura funcional amplia de dominios (legal, compliance, comercio, educacion, logistica).
- CI con gates de lint, smoke, quality, metadata y tests por carpeta.
- Requiere entorno de dependencias correcto para ejecutar todas las suites del monorepo.

## Estructura vigente

- `portfolio/`: demos publicas orientadas a casos de uso.
- `products/`: agentes y orquestadores mas cercanos a producto.
- `core/`: utilidades compartidas.
- `scripts/`: checks de CI y validacion local.
- `tests/`: pruebas minimas de estructura y contrato.

## Proyectos destacados

- `portfolio/p01-inteligencia-comercial-internacional`
- `portfolio/p05-rag-documentacion-interna`
- `products/agente-obligaciones-contractuales`

## Demos complementarias

- `portfolio/p02-agente-multi-herramienta`
- `portfolio/p03-agente-licitaciones`
- `portfolio/p04-agente-rrhh-candidatos`
- `portfolio/p06-rag-contratos-legales`
- `portfolio/p07-chatbot-atencion-cliente`
- `portfolio/p08-rag-normativa-comercio`
- `portfolio/p09-evaluador-ideas-negocio`
- `portfolio/p10-dashboard-lenguaje-natural`

## Laboratorio tecnico

- `products/agente-logistica-autonoma`
- `products/agente-cumplimiento-politicas`
- `products/agente-inteligencia-geopolitica`
- `products/asistente-legal-supervisado`
- `products/orquestador-psicoeducativo`
- `products/orquestador-integridad-educativa`
- `products/orquestador-coaching-cambio`
- `products/agente-evidencias-auditoria`

## Lectura recomendada

1. `README.md`
2. Este `CATALOGO.md`
3. Los tres proyectos destacados
4. Demos complementarias
5. Laboratorio tecnico

## Reglas de mantenimiento

- Mantener `.env.example` sin secretos reales.
- No versionar artefactos locales de runtime.
- Endurecer pruebas y cobertura en proyectos que evolucionen a producto.
- Verificar rotacion de claves antes de cualquier publicacion.

## Licencia y autoria

Publicado bajo licencia Creative Commons CC BY-SA 4.0 International.

(c) 2026 - Jose Maria Tinajero Rios.
