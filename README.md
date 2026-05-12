# Portfolio IA Aplicada

Monorepo tecnico de agentes de IA (*Artificial Intelligence – Inteligencia Artificial*) aplicada a negocio, documentacion, comercio exterior, cumplimiento normativo y automatizacion empresarial.

Este repositorio no se plantea como una web publica ni como una landing comercial. Es la base tecnica del portfolio: demos ejecutables, productos con vocacion de uso real, utilidades compartidas, validaciones y documentacion de apoyo.

## Enfoque

- Resolver problemas empresariales concretos, no acumular demos genericas.
- Priorizar trazabilidad, limites claros y supervision humana cuando el dominio lo exige.
- Separar prototipos publicos de agentes con estructura de producto.
- Mantener una base sencilla de ejecutar, revisar y evolucionar.

## Mapa rapido

- `core/`: utilidades compartidas y piezas reutilizables.
- `portfolio/`: demos y prototipos publicos orientados a casos de uso concretos.
- `products/`: agentes y orquestadores con estructura de producto.
- `scripts/`: checks de CI (*Continuous Integration – Integracion Continua*) y utilidades de validacion.
- `tests/`: pruebas minimas del portfolio y validaciones de estructura.

## Proyectos destacados

- `portfolio/p01-inteligencia-comercial-internacional`: inteligencia comercial internacional para comparar paises, sectores y oportunidades de mercado.
- `portfolio/p05-rag-documentacion-interna`: RAG (*Retrieval-Augmented Generation – Generacion Aumentada por Recuperacion*) para consulta de documentacion interna.
- `products/agente-obligaciones-contractuales`: agente supervisado de obligaciones contractuales, evidencias, riesgos y exportes.

El estado completo por proyecto esta documentado en [CATALOGO.md](CATALOGO.md).

## Estado actual

- El codigo ejecutable principal vive en `portfolio/` y `products/`.
- `portfolio/` queda reservado para demos de portfolio.
- `products/` queda reservado para agentes con vocacion de producto.
- La CI valida estructura, compilacion Python, tests minimos del portfolio y tests de productos por carpeta.
- `proyectos/` queda retirado como carpeta valida; `portfolio/` es la ruta canonica.

## Checks locales

```powershell
.venv\Scripts\python.exe scripts/ci_lint.py
.venv\Scripts\python.exe scripts/ci_smoke.py
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts/ci_products.py
```

## Politica del repositorio

- No versionar secretos (`.env`) ni artefactos de runtime.
- No versionar entornos virtuales, caches, bases vectoriales ni exports locales.
- Mantener un `README.md`, `requirements.txt` y entrypoint claro por proyecto.
- Documentar siempre los limites de uso cuando el agente opere en dominios sensibles.
- Separar con claridad demo, prototipo, laboratorio y producto.

## Lectura recomendada

1. Revisar primero [CATALOGO.md](CATALOGO.md).
2. Entrar despues en los tres proyectos destacados.
3. Usar el resto del repositorio como evidencia tecnica y laboratorio de evolucion.
---

## 🧪 Proyectos Complementarios (Demos Rápidas)

Agentes independientes optimizados para validación ejecutable en <90 segundos, sin configuración compleja:

| Agente | Enfoque | Comando | Enlace |
|--------|---------|---------|--------|
| 💰 [agente-finanzas-pyme](https://github.com/chema74/agente-finanzas-pyme) | Detección de anomalías + XAI | `powershell -File scripts/demo/run_demo.ps1` | [Ver repo](https://github.com/chema74/agente-finanzas-pyme) |
| 🌱 [agente-esg-reporting](https://github.com/chema74/agente-esg-reporting) | Reporting ESG + trazabilidad CSRD | `powershell -File scripts/demo/run_demo.ps1` | [Ver repo](https://github.com/chema74/agente-esg-reporting) |

> Estos proyectos comparten filosofía local-first y open-source, pero están optimizados para validación rápida. Este monorepo (`Agentes_IA`) prioriza arquitectura modular, trazabilidad y evolución técnica sobre velocidad de demo.

---

## 📊 Visualización de Agentes

Los agentes incluyen dashboards interactivos para visualización de resultados.

### Ejemplo: Contract Obligations Agent

```powershell
cd products/agente-obligaciones-contractuales
streamlit run app.py
## 🪪 Licencia y Autoría

Publicado bajo licencia Creative Commons CC BY-SA 4.0 International.  
© 2025 – Txema Ríos. Todos los derechos compartidos.
