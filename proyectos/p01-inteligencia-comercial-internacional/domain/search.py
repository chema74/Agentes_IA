"""
search.py

Responsabilidad:
realizar búsquedas web estructuradas por dimensiones y,
además, conservar una lista trazable de fuentes.

Esto mejora:
- trazabilidad
- explicabilidad
- credibilidad del sistema
"""

from __future__ import annotations

from typing import Dict, List, Any

from tavily import TavilyClient

from config.settings import MAX_RESULTS_PER_QUERY, SEARCH_DEPTH


def buscar_info(tavily: TavilyClient, pais: str, sector: str) -> Dict[str, Any]:
    """
    Busca información estructurada del país por dimensiones y devuelve
    tanto el contexto textual como las fuentes utilizadas.
    """
    if tavily is None:
        raise ValueError("El cliente Tavily no puede ser None.")

    pais = (pais or "").strip()
    sector = (sector or "").strip()

    if not pais:
        raise ValueError("El parámetro 'pais' es obligatorio.")
    if not sector:
        raise ValueError("El parámetro 'sector' es obligatorio.")

    queries = {
        "politico": (
            f"situación política {pais} estabilidad gobierno "
            f"riesgo político {pais} actualidad"
        ),
        "economico": (
            f"economía {pais} inflación PIB crecimiento "
            f"indicadores económicos {pais} actualidad"
        ),
        "regulatorio": (
            f"exportar a {pais} aranceles regulación requisitos "
            f"empresas extranjeras comercio internacional"
        ),
        "oportunidades": (
            f"oportunidades negocio {pais} sector {sector} "
            f"inversión mercado exportación"
        ),
    }

    contexto: Dict[str, str] = {}
    fuentes: List[Dict[str, str]] = []

    for categoria, query in queries.items():
        try:
            resultado = tavily.search(
                query=query,
                max_results=MAX_RESULTS_PER_QUERY,
                search_depth=SEARCH_DEPTH,
                include_raw_content=False,
            )
        except Exception as e:
            contexto[categoria] = (
                f"Error al consultar información para la categoría '{categoria}': {e}"
            )
            continue

        results = resultado.get("results", []) if isinstance(resultado, dict) else []
        fragmentos: List[str] = []

        for r in results:
            titulo = str(r.get("title", "") or "").strip()
            contenido = str(r.get("content", "") or "").strip()
            url = str(r.get("url", "") or "").strip()

            if contenido:
                contenido = contenido[:300]

            fragmento = (
                f"- Título: {titulo or 'Sin título'}\n"
                f"  Resumen: {contenido or 'Sin resumen disponible'}\n"
                f"  URL: {url or 'Sin URL disponible'}"
            )
            fragmentos.append(fragmento)

            fuentes.append(
                {
                    "categoria": categoria,
                    "titulo": titulo,
                    "url": url,
                    "resumen": contenido,
                }
            )

        if not fragmentos:
            contexto[categoria] = "No se encontraron resultados relevantes."
        else:
            contexto[categoria] = "\n".join(fragmentos)

    return {
        "contexto": contexto,
        "fuentes": fuentes,
    }