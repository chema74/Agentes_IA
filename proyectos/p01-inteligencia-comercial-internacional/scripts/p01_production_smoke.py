"""
Smoke runner de producción para P01.

Objetivo:
- validar con pocas llamadas reales que el pipeline sigue funcionando en modo production
- capturar fallos por etapa con mensajes cortos y útiles
- reutilizar el pipeline actual sin refactors de arquitectura

Casos disponibles:
- single: una sola validación de país-sector
- compare: comparación mínima de dos países
- ranking: ranking mínimo de dos países con persistencia local
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter, sleep
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.streamlit_app import _save_ranking_history, construir_resultado_pais, validar_configuracion_api  # noqa: E402
from config import settings  # noqa: E402
from domain.scoring import get_official_score  # noqa: E402
from infrastructure.clients import get_clients  # noqa: E402

DEFAULT_COUNTRY_A = "México"
DEFAULT_COUNTRY_B = "Alemania"
DEFAULT_SECTOR = "Tecnología"
DEFAULT_COMPANY_TYPE = "PYME"


def _assert_production_mode() -> None:
    """Bloquea el runner si no se está validando en production."""
    app_mode = getattr(settings, "APP_MODE", "").strip().lower()
    if app_mode != "production":
        raise RuntimeError(f"Este runner exige APP_MODE=production y ahora mismo vale '{app_mode}'.")


def _build_clients() -> tuple[object, object]:
    """Valida credenciales y crea clientes reales con el menor coste posible."""
    validar_configuracion_api()
    return get_clients()


def _print_header(case_name: str) -> None:
    print(f"\n=== P01 production smoke: {case_name} ===")


def _result_to_dict(resultado: Any) -> dict[str, Any] | None:
    """Normaliza la respuesta al formato dict esperado por el smoke."""
    if isinstance(resultado, dict):
        return resultado

    if hasattr(resultado, "model_dump"):
        try:
            dump = resultado.model_dump()
            if isinstance(dump, dict):
                return dump
        except Exception:
            pass

    if isinstance(resultado, str):
        texto = resultado.strip()
        if texto:
            try:
                parsed = json.loads(texto)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

    try:
        convertido = dict(resultado)
        if isinstance(convertido, dict):
            return convertido
    except Exception:
        pass

    return None


def _assert_minimum_shape(result: dict[str, Any]) -> None:
    """Comprueba la forma mínima útil para producción."""
    claves_criticas = ("resumen_ejecutivo", "alertas", "oportunidades")
    faltantes = [key for key in claves_criticas if key not in result]
    if faltantes:
        raise RuntimeError(f"Faltan claves narrativas mínimas: {', '.join(faltantes)}.")

    scores_agregados = result.get("scores_agregados")
    if not isinstance(scores_agregados, dict) or "score_total" not in scores_agregados:
        raise RuntimeError("No aparece scores_agregados.score_total en la forma esperada.")


def _summarize_result(country: str, result: dict[str, Any]) -> None:
    score_total = get_official_score(result)
    resumen = str(result.get("resumen_ejecutivo", "")).strip()
    alertas = result.get("alertas", [])
    oportunidades = result.get("oportunidades", [])
    fuentes = result.get("fuentes", [])
    parser_ok = all(key in result for key in ("scores", "scores_agregados", "justificacion_scores"))

    print(f"- país: {country}")
    print(f"- score_total: {score_total:.2f}")
    print(f"- parser_ok: {'sí' if parser_ok else 'no'}")
    print(f"- alertas: {len(alertas) if isinstance(alertas, list) else 'no_lista'}")
    print(f"- oportunidades: {len(oportunidades) if isinstance(oportunidades, list) else 'no_lista'}")
    print(f"- fuentes: {len(fuentes) if isinstance(fuentes, list) else 'no_lista'}")
    print(f"- resumen: {resumen[:160]}")


def run_single() -> int:
    """Caso 1: una sola llamada real para validar credenciales, proveedor y parser."""
    _print_header("single")
    tavily, groq = _build_clients()

    start = perf_counter()
    raw_result = construir_resultado_pais(
        tavily=tavily,
        groq=groq,
        pais=DEFAULT_COUNTRY_A,
        sector=DEFAULT_SECTOR,
        tipo_empresa=DEFAULT_COMPANY_TYPE,
        lang="es",
        force_refresh=True,
    )
    elapsed = perf_counter() - start

    result = _result_to_dict(raw_result)
    if result is None:
        raise RuntimeError("La respuesta single no devolvió un dict válido.")

    _assert_minimum_shape(result)
    _summarize_result(DEFAULT_COUNTRY_A, result)
    print(f"- tiempo_total_segundos: {elapsed:.2f}")
    return 0


def run_compare() -> int:
    """Caso 2: dos llamadas reales para validar comparación y consistencia básica."""
    _print_header("compare")
    tavily, groq = _build_clients()

    start = perf_counter()
    raw_result_a = construir_resultado_pais(
        tavily=tavily,
        groq=groq,
        pais=DEFAULT_COUNTRY_A,
        sector=DEFAULT_SECTOR,
        tipo_empresa=DEFAULT_COMPANY_TYPE,
        lang="es",
        force_refresh=True,
    )

    if getattr(settings, "THROTTLING_DELAY", 0) > 0:
        sleep(settings.THROTTLING_DELAY)

    raw_result_b = construir_resultado_pais(
        tavily=tavily,
        groq=groq,
        pais=DEFAULT_COUNTRY_B,
        sector=DEFAULT_SECTOR,
        tipo_empresa=DEFAULT_COMPANY_TYPE,
        lang="es",
        force_refresh=True,
    )
    elapsed = perf_counter() - start

    result_a = _result_to_dict(raw_result_a)
    result_b = _result_to_dict(raw_result_b)
    if result_a is None or result_b is None:
        raise RuntimeError("La comparación no devolvió dos resultados válidos.")

    _assert_minimum_shape(result_a)
    _assert_minimum_shape(result_b)

    score_a = get_official_score(result_a)
    score_b = get_official_score(result_b)

    _summarize_result(DEFAULT_COUNTRY_A, result_a)
    _summarize_result(DEFAULT_COUNTRY_B, result_b)
    print(f"- delta_score_total: {score_a - score_b:+.2f}")
    print(f"- tiempo_total_segundos: {elapsed:.2f}")
    return 0


def run_ranking() -> int:
    """Caso 3: ranking mínimo con persistencia local del histórico."""
    _print_header("ranking")
    tavily, groq = _build_clients()

    start = perf_counter()
    resultados = []
    for country in (DEFAULT_COUNTRY_A, DEFAULT_COUNTRY_B):
        raw_result = construir_resultado_pais(
            tavily=tavily,
            groq=groq,
            pais=country,
            sector=DEFAULT_SECTOR,
            tipo_empresa=DEFAULT_COMPANY_TYPE,
            lang="es",
            force_refresh=True,
        )

        result = _result_to_dict(raw_result)
        if result is None:
            raise RuntimeError(f"El ranking no pudo construir el resultado de {country}.")

        _assert_minimum_shape(result)
        resultados.append(
            {
                "pais": country,
                "score": get_official_score(result),
                "resultado": result,
            }
        )

        if getattr(settings, "THROTTLING_DELAY", 0) > 0 and country != DEFAULT_COUNTRY_B:
            sleep(settings.THROTTLING_DELAY)

    resultados = sorted(resultados, key=lambda item: item["score"])
    run_id = _save_ranking_history(
        resultados_ordenados=resultados,
        sector=DEFAULT_SECTOR,
        tipo_empresa=DEFAULT_COMPANY_TYPE,
        countries_requested=[DEFAULT_COUNTRY_A, DEFAULT_COUNTRY_B],
    )
    elapsed = perf_counter() - start

    if not run_id:
        raise RuntimeError("No se pudo persistir el histórico del ranking.")

    print(f"- run_id: {run_id}")
    print(f"- países_persistidos: {len(resultados)}")
    print(f"- tiempo_total_segundos: {elapsed:.2f}")
    print("- histórico: guardado correctamente")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke runner de producción para P01.")
    parser.add_argument(
        "case",
        choices=("single", "compare", "ranking"),
        help="Caso mínimo a ejecutar contra APIs reales.",
    )
    args = parser.parse_args()

    _assert_production_mode()

    if args.case == "single":
        return run_single()
    if args.case == "compare":
        return run_compare()
    return run_ranking()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}")
        if getattr(settings, "DEBUG_MODE", False):
            raise
        raise SystemExit(1)
