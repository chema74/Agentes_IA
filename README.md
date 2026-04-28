# Portfolio IA Aplicada

Monorepo con una web publica en la raiz, prototipos de portfolio en `portfolio/` y agentes mas maduros en `products/`.

## Mapa rapido

- `assets/`: CSS, JavaScript y recursos de la web publica.
- `core/`: utilidades compartidas.
- `portfolio/`: 10 demos y prototipos publicos.
- `products/`: 9 agentes y orquestadores con estructura de producto.
- `scripts/`: checks de CI y utilidades de validacion.
- `tests/`: pruebas minimas del portfolio.

## Estado actual

- La web publica vive en la raiz (`index.html`, `proyectos.html`, `contacto.html`, etc.).
- El codigo ejecutable principal vive en `portfolio/` y `products/`.
- La CI valida estructura, compilacion Python, tests minimos del portfolio y tests de productos por carpeta.
- `proyectos/` queda retirado como carpeta valida; `portfolio/` es la ruta canonica.

## Checks locales

```powershell
.venv\Scripts\python.exe scripts/ci_lint.py
.venv\Scripts\python.exe scripts/ci_smoke.py
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts/ci_products.py
```

## Catalogo

El estado por proyecto y lo pendiente para cierre final esta en [CATALOGO.md](CATALOGO.md).

## Politica del repositorio

- No versionar secretos (`.env`) ni artefactos de runtime.
- No versionar entornos virtuales, caches, bases vectoriales ni exports locales.
- Mantener un `README.md`, `requirements.txt` y entrypoint claro por proyecto.
- Reservar `portfolio/` para demos y `products/` para agentes con vocacion de producto.
