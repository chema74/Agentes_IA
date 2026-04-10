"""
Aplicacion publica de P01.

Base publica actual del agente final "Agente de inteligencia comercial internacional".
La app permite comparar paises y mercados con senales orientativas obtenidas a partir
 de busquedas web, scoring asistido por LLM y analisis estructurado.
"""

from __future__ import annotations

import os
import sys
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.clients import get_clients
from infrastructure.retry import with_retry
from domain.search import buscar_info
from domain.analysis import analizar_pais
from domain.parser import clean_json
from domain.scoring import OFFICIAL_SCORE_LABEL, calcular_scores, get_official_score
from domain.i18n import get_text
from domain.demo_data import (
    get_demo_result,
    get_demo_supported_countries,
    split_demo_supported_countries,
)
from domain.dashboard import (
    build_dashboard_rows,
    DIMENSIONES_DASHBOARD,
    compute_ranking_medio_por_pais,
    compute_dispersion_scores,
)
from domain import history
from domain.cache import (
    load_country_analysis_from_cache,
    save_country_analysis_to_cache,
    clear_country_analysis_cache,
)
from domain.logger import log_event
from domain.schemas import RankingItem, RankingMetadata, RankingResult, SourceItem
from domain.validators import (
    parse_and_validate_ranking_countries,
    validate_comparison_inputs,
    validate_sector_input,
    validate_tipo_empresa_input,
)
from config.settings import (
    APP_MODE,
    DEBUG_MODE,
    DEFAULT_COUNTRY,
    THROTTLING_DELAY,
    SCORING_WEIGHTS,
    COUNTRY_VS_SECTOR_WEIGHTS,
    validar_configuracion_api as validar_configuracion_api_config,
)


PAISES_DEMO = get_demo_supported_countries()


def validar_configuracion_api() -> None:
    """Compatibilidad hacia atrás: delega la validación centralizada."""
    validar_configuracion_api_config()


def calcular_score_total(resultado: Dict[str, Any]) -> float:
    """
    Alias de compatibilidad hacia atras.

    Paso 1: reutiliza el helper oficial del dominio.
    Paso 2: evita mantener formulas paralelas en la UI.
    """
    return get_official_score(resultado)


def _build_demo_unavailable_message(paises: list[str]) -> str:
    """
    Construye un mensaje claro para países no soportados en modo demo.
    """
    paises_txt = ", ".join(paises)
    return (
        f"Estos países no están disponibles en modo demo: {paises_txt}. "
        "Usa uno de los países soportados o cambia a modo producción."
    )


def _build_demo_internal_error_message(paises: list[str]) -> str:
    """
    Construye un mensaje específico para fallos internos del modo demo.
    """
    paises_txt = ", ".join(paises)
    return (
        f"Se produjo un error interno al generar los datos demo para: {paises_txt}. "
        "Revisa los fixtures demo o el pipeline local."
    )


def _get_demo_catalog_text() -> str:
    """
    Devuelve el catálogo demo en texto legible para mostrarlo en la UI.
    """
    return ", ".join(PAISES_DEMO)


def _parse_ranking_countries_input(raw_text: str) -> tuple[list[str], list[str]]:
    """
    Normaliza el input del ranking para aceptar saltos de línea o comas.
    """
    texto_normalizado = raw_text.replace("\r\n", "\n").replace("\n", ",")
    return parse_and_validate_ranking_countries(texto_normalizado)


def _save_ranking_history(
    resultados_ordenados: list[dict[str, Any]],
    sector: str,
    tipo_empresa: str,
    countries_requested: list[str],
) -> Optional[str]:
    """
    Persiste un ranking generado para que el dashboard pueda leer historial.

    Paso 1: construir un RankingResult mínimo y compatible con history.py.
    Paso 2: guardar el run en `history/` con su `ranking.json` y `manifest.json`.
    """
    try:
        run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        metadata = RankingMetadata(
            run_id=run_id,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sector=sector,
            company_type=tipo_empresa,
            countries_requested=countries_requested,
            total_countries=len(resultados_ordenados),
            version="streamlit-app",
        )

        ranking_items: list[RankingItem] = []
        for idx, entry in enumerate(resultados_ordenados, start=1):
            resultado = entry.get("resultado", {}) if isinstance(entry, dict) else {}
            fuentes_raw = resultado.get("fuentes", []) if isinstance(resultado, dict) else []

            fuentes = [
                SourceItem(
                    category=str(f.get("categoria", "")),
                    title=str(f.get("titulo", "")),
                    url=str(f.get("url", "")),
                    summary=str(f.get("resumen", "")),
                )
                for f in fuentes_raw
                if isinstance(f, dict)
            ]

            ranking_items.append(
                RankingItem(
                    position=idx,
                    country=str(entry.get("pais", "")),
                    score_total=float(entry.get("score", 0.0)),
                    dimension_scores=resultado.get("scores", {}) if isinstance(resultado, dict) else {},
                    executive_summary=str(resultado.get("resumen_ejecutivo", "")) if isinstance(resultado, dict) else "",
                    sources=fuentes,
                    raw_result=resultado if isinstance(resultado, dict) else {},
                )
            )

        ranking_result = RankingResult(metadata=metadata, ranking=ranking_items)
        history.save_ranking_run(ranking_result=ranking_result, artifact_paths={})
        return run_id
    except Exception as exc:
        log_event(
            "ranking_history_save_failed",
            {
                "error": str(exc),
                "sector": sector,
                "tipo_empresa": tipo_empresa,
            },
        )
        if DEBUG_MODE:
            print(traceback.format_exc())
        return None


def construir_resultado_pais(
    tavily: Any,
    groq: Any,
    pais: str,
    sector: str,
    tipo_empresa: str,
    lang: str,
    force_refresh: bool = False,
) -> Optional[Dict[str, Any]]:
    """Construye el analisis de un pais en modo demo o produccion."""
    if APP_MODE == "demo":
        try:
            resultado_demo = get_demo_result(pais, sector, tipo_empresa)
            if resultado_demo is not None:
                resultado_demo["_demo_mode"] = True
                log_event("demo_result_served", {"pais": pais, "sector": sector})
                return resultado_demo
        except Exception as exc:
            log_event("demo_result_error", {"pais": pais, "sector": sector, "error": str(exc)})
            if DEBUG_MODE:
                print(traceback.format_exc())
            return None
        log_event("demo_pais_no_disponible", {"pais": pais})
        return None

    if not force_refresh:
        cached = load_country_analysis_from_cache(pais=pais, sector=sector, tipo_empresa=tipo_empresa)
        if cached:
            res = cached.get("result", {})
            if isinstance(res, dict):
                res["_cache_used"] = True
                log_event("cache_hit", {"pais": pais, "sector": sector})
                return res

    try:
        busqueda = with_retry(lambda: buscar_info(tavily, pais, sector), label=f"Tavily:{pais}")
        if not isinstance(busqueda, dict):
            raise ValueError("La busqueda no devolvio un resultado valido.")

        contexto = busqueda.get("contexto", {})
        fuentes = busqueda.get("fuentes", [])
        if not isinstance(contexto, dict):
            raise ValueError("El contexto recuperado no tiene un formato valido.")
        if not isinstance(fuentes, list):
            fuentes = []

        scoring = with_retry(lambda: calcular_scores(contexto, groq=groq), label=f"Scoring:{pais}")
        raw_narrativa = with_retry(
            lambda: analizar_pais(groq, pais, sector, tipo_empresa, contexto),
            label=f"LLM:{pais}",
        )
        data = clean_json(raw_narrativa)
        if not isinstance(data, dict):
            raise ValueError("El analisis narrativo no devolvio un bloque estructurado valido.")

        data.update(
            {
                "scores": scoring.get("scores", {}),
                "scores_agregados": scoring.get("scores_agregados", {}),
                "justificacion_scores": scoring.get("justificacion_scores", {}),
                "cobertura_evidencia": scoring.get("cobertura_evidencia", {}),
                "bandas_confianza": scoring.get("bandas_confianza", {}),
                "fuentes": fuentes,
                "sector": sector,
                "tipo_empresa": tipo_empresa,
                "_scoring_fallback": scoring.get("_scoring_fallback", False),
                "_scoring_error": scoring.get("_scoring_error"),
                "_cache_used": False,
            }
        )

        save_country_analysis_to_cache(pais, sector, tipo_empresa, data)
        log_event(
            "analysis_completed",
            {
                "pais": pais,
                "sector": sector,
                "tipo_empresa": tipo_empresa,
                "num_fuentes": len(fuentes),
            },
        )
        return data
    except Exception as exc:
        tb = traceback.format_exc()
        log_event(
            "analysis_failed",
            {
                "pais": pais,
                "sector": sector,
                "tipo_empresa": tipo_empresa,
                "error": str(exc),
                "traceback": tb if DEBUG_MODE else "",
            },
        )
        if DEBUG_MODE:
            print(tb)
        return None


def mostrar_resultado_pais(titulo: str, resultado: Dict[str, Any], lang: str) -> None:
    """Presentacion de resultados de un pais."""
    st.subheader(titulo)

    if resultado.get("_demo_mode"):
        st.info("Modo demo: datos precalculados sin llamadas a APIs reales.")
    elif resultado.get("_cache_used"):
        st.caption(f"Resultados recuperados de cache. {get_text('cache_hit_msg', lang=lang)}")

    st.markdown(f"**{get_text('summary_title', lang=lang)}**")
    st.write(resultado.get("resumen_ejecutivo", "No disponible"))

    scores = resultado.get("scores", {})
    if scores:
        st.markdown(f"**{get_text('scores_title', lang=lang)}**")
        df_display = pd.DataFrame(
            [{"Dimension": k.replace("_", " ").capitalize(), "Senal": v} for k, v in scores.items()]
        )
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.caption(
            "Las senales mostradas son orientativas y sirven como apoyo a la comparacion, "
            "no como rating formal de riesgo pais. En el indice orientativo de riesgo, menor score implica mejor posicion relativa."
        )


def modo_comparacion(lang: str) -> None:
    """Comparacion entre dos mercados."""
    st.subheader(get_text("menu_compare", lang=lang))

    with st.expander(get_text("compare_config_title", lang=lang), expanded=True):
        c1, c2 = st.columns(2)

        if APP_MODE == "demo":
            st.caption(f"Países soportados en demo: {_get_demo_catalog_text()}")
            default_idx_b = min(2, len(PAISES_DEMO) - 1) if len(PAISES_DEMO) > 1 else 0
            pais_a_raw = c1.selectbox(f"{get_text('country_label', lang=lang)} A", PAISES_DEMO, index=0)
            pais_b_raw = c2.selectbox(f"{get_text('country_label', lang=lang)} B", PAISES_DEMO, index=default_idx_b)
        else:
            pais_a_raw = c1.text_input(f"{get_text('country_label', lang=lang)} A", value=DEFAULT_COUNTRY)
            pais_b_raw = c2.text_input(f"{get_text('country_label', lang=lang)} B", value="Marruecos")

        sectores = get_text("sectors", section="domain", lang=lang)
        tipos = get_text("company_types", section="domain", lang=lang)
        col_s, col_t = st.columns(2)
        sector_sel = col_s.selectbox(get_text("sector_label", lang=lang), sectores)
        tipo_sel = col_t.selectbox(get_text("company_type_label", lang=lang), tipos)

    if st.button(get_text("btn_compare", lang=lang), use_container_width=True):
        p_a, p_b, err_p = validate_comparison_inputs(pais_a_raw, pais_b_raw)
        s_c, err_s = validate_sector_input(sector_sel, lang=lang)
        t_c, err_t = validate_tipo_empresa_input(tipo_sel, lang=lang)
        all_errs = err_p + err_s + err_t
        if all_errs:
            for err in all_errs:
                st.error(err)
            return

        if APP_MODE == "demo":
            paises_demo_validos, paises_demo_no_disponibles = split_demo_supported_countries([p_a, p_b])
            if paises_demo_no_disponibles:
                st.error(_build_demo_unavailable_message(paises_demo_no_disponibles))
                return
            p_a, p_b = paises_demo_validos

        try:
            validar_configuracion_api()
            tavily, groq = get_clients()
        except Exception as exc:
            log_event("client_initialization_error", {"contexto": "modo_comparacion", "error": str(exc)})
            st.error(f"No se pudieron inicializar los clientes necesarios para el analisis: {exc}")
            if DEBUG_MODE:
                st.exception(exc)
            return

        with st.spinner(get_text("analyzing_msg", lang=lang)):
            res_a = construir_resultado_pais(tavily, groq, p_a, s_c, t_c, lang, force_refresh=False)
            if APP_MODE == "production" and THROTTLING_DELAY > 0:
                time.sleep(THROTTLING_DELAY)
            res_b = construir_resultado_pais(tavily, groq, p_b, s_c, t_c, lang, force_refresh=False)

        if res_a and res_b:
            st.session_state.resultado_a = res_a
            st.session_state.p_a = p_a
            st.session_state.resultado_b = res_b
            st.session_state.p_b = p_b
            st.success(get_text("comparison_ready_msg", lang=lang))
            st.rerun()
        else:
            if not res_a:
                if APP_MODE == "demo":
                    st.error(_build_demo_internal_error_message([p_a]))
                else:
                    st.error(
                        f"No se pudo completar el analisis de {p_a}. Revisa el pais, el sector o las claves API y vuelve a intentarlo."
                    )
            if not res_b:
                if APP_MODE == "demo":
                    st.error(_build_demo_internal_error_message([p_b]))
                else:
                    st.error(
                        f"No se pudo completar el analisis de {p_b}. Revisa el pais, el sector o las claves API y vuelve a intentarlo."
                    )

    if st.session_state.get("resultado_a") and st.session_state.get("resultado_b"):
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            mostrar_resultado_pais(f"📊 {st.session_state.p_a}", st.session_state.resultado_a, lang)
        with c2:
            mostrar_resultado_pais(f"📊 {st.session_state.p_b}", st.session_state.resultado_b, lang)

        st.markdown("---")
        st.subheader(get_text("comparative_analysis", lang=lang))
        st.caption(
            "Comparacion orientativa basada en senales recuperadas y analisis asistido por modelo. "
            "Menor score implica mejor posicion relativa. No sustituye due diligence comercial, regulatoria o juridica."
        )
        st.caption(
            "El indice orientativo de riesgo es una estimacion exploratoria y no un rating certificado."
        )

        score_a = get_official_score(st.session_state.resultado_a)
        score_b = get_official_score(st.session_state.resultado_b)
        col_v1, col_v2 = st.columns(2)
        col_v1.metric(
            f"{st.session_state.p_a} · {OFFICIAL_SCORE_LABEL}",
            f"{score_a:.1f}/10",
            delta=f"{score_a - score_b:+.1f}" if score_b != 0 else None,
            delta_color="inverse",
        )
        col_v2.metric(
            f"{st.session_state.p_b} · {OFFICIAL_SCORE_LABEL}",
            f"{score_b:.1f}/10",
            delta=f"{score_b - score_a:+.1f}" if score_a != 0 else None,
            delta_color="inverse",
        )


def modo_ranking(lang: str) -> None:
    """Genera una priorizacion orientativa de varios paises."""
    st.subheader(get_text("menu_ranking", lang=lang))
    st.caption(
        "Este ranking es una ayuda para priorizar mercados de forma comparativa. "
        "Menor score implica mejor posicion relativa. No equivale a un rating formal ni a una evaluacion exhaustiva de entrada a pais."
    )

    with st.expander("Configuracion del ranking", expanded=True):
        countries_input = st.text_area("Introduce paises (uno por linea)", value="Espana\nFrancia\nAlemania", height=100)
        if APP_MODE == "demo":
            st.caption(f"Catálogo demo soportado: {_get_demo_catalog_text()}")
        sectores = get_text("sectors", section="domain", lang=lang)
        sector_sel = st.selectbox("Sector", sectores)
        tipos = get_text("company_types", section="domain", lang=lang)
        tipo_sel = st.selectbox("Tipo de empresa", tipos)

        if st.button("Generar ranking", use_container_width=True):
            countries, errores_paises = _parse_ranking_countries_input(countries_input)
            if errores_paises:
                for error in errores_paises:
                    st.error(error)
                return

            paises_demo_no_disponibles: list[str] = []
            if APP_MODE == "demo":
                countries, paises_demo_no_disponibles = split_demo_supported_countries(countries)
                if paises_demo_no_disponibles:
                    st.warning(_build_demo_unavailable_message(paises_demo_no_disponibles))
                if len(countries) < 2:
                    st.error(
                        "En modo demo necesitas al menos dos países soportados para generar ranking."
                    )
                    return

            try:
                validar_configuracion_api()
                tavily, groq = get_clients()
            except Exception as exc:
                log_event("client_initialization_error", {"contexto": "modo_ranking", "error": str(exc)})
                st.error(f"No se pudieron inicializar los clientes necesarios para el ranking: {exc}")
                if DEBUG_MODE:
                    st.exception(exc)
                return

            with st.spinner("Analizando paises..."):
                resultados = []
                errores_internos_demo = []
                fallos_pipeline = []
                for i, pais in enumerate(countries):
                    resultado = construir_resultado_pais(tavily, groq, pais, sector_sel, tipo_sel, lang, force_refresh=False)
                    if resultado:
                        resultados.append(
                            {
                                "pais": pais,
                                "score": get_official_score(resultado),
                                "resultado": resultado,
                            }
                        )
                    else:
                        if APP_MODE == "demo":
                            errores_internos_demo.append(pais)
                        else:
                            fallos_pipeline.append(pais)
                    if APP_MODE == "production" and THROTTLING_DELAY > 0 and i < len(countries) - 1:
                        time.sleep(THROTTLING_DELAY)

            if resultados:
                resultados_ordenados = sorted(resultados, key=lambda x: x["score"])
                st.session_state.ranking_resultados = resultados_ordenados
                run_id = _save_ranking_history(
                    resultados_ordenados=resultados_ordenados,
                    sector=sector_sel,
                    tipo_empresa=tipo_sel,
                    countries_requested=countries,
                )
                df_ranking = pd.DataFrame(
                    [
                        {"Posicion": i + 1, "Pais": r["pais"], OFFICIAL_SCORE_LABEL.title(): f"{r['score']:.2f}/10"}
                        for i, r in enumerate(resultados_ordenados)
                    ]
                )
                st.dataframe(df_ranking, use_container_width=True, hide_index=True)
                st.success(f"Ranking generado con {len(resultados_ordenados)} paises.")
                if run_id:
                    st.caption(f"Histórico guardado con run_id: {run_id}")
                else:
                    st.warning("No se pudo guardar este ranking en el histórico local.")
                if paises_demo_no_disponibles:
                    st.info(
                        "Se omitieron países no soportados por el catálogo demo y se continuó con los disponibles."
                    )
                if errores_internos_demo:
                    st.error(_build_demo_internal_error_message(errores_internos_demo))
            else:
                if APP_MODE == "demo" and paises_demo_no_disponibles and not errores_internos_demo:
                    st.error(_build_demo_unavailable_message(paises_demo_no_disponibles))
                elif APP_MODE == "demo" and errores_internos_demo:
                    st.error(_build_demo_internal_error_message(errores_internos_demo))
                elif fallos_pipeline:
                    st.error(
                        f"No se pudo completar el análisis de estos países: {', '.join(fallos_pipeline)}."
                    )
                else:
                    st.error("No se pudo completar el analisis de los paises indicados.")


def mostrar_dashboard_panel(lang: str) -> None:
    """Panel historico con metricas agregadas."""
    st.subheader(get_text("menu_dashboard", lang=lang))
    st.caption(
        "Panel historico para revisar resultados previos guardados por la aplicacion. "
        "Usalo como apoyo analitico interno. Menor score implica mejor posicion relativa."
    )
    st.caption(
        "Si cambia la metodologia o los pesos, la comparabilidad historica puede verse afectada."
    )

    try:
        rows = build_dashboard_rows()
    except Exception as exc:
        st.error(f"No se pudo cargar el historial de analisis: {exc}")
        if DEBUG_MODE:
            st.exception(exc)
        return

    if not rows:
        st.warning("Todavía no hay análisis guardados en esta instalación.")
        st.info(
            "Genera primero un ranking desde la app para poblar el histórico que consume este dashboard."
        )
        return

    df = pd.DataFrame(rows)
    tab_evol, tab_avg, tab_src, tab_vol, tab_mean = st.tabs(
        [
            get_text("tab_evolution", lang=lang),
            get_text("tab_average", lang=lang),
            get_text("tab_sources", lang=lang),
            get_text("tab_volatility", lang=lang),
            get_text("tab_ranking_medio", lang=lang),
        ]
    )

    with tab_evol:
        st.markdown(f"### Evolucion del {OFFICIAL_SCORE_LABEL}")
        if {"score_total", "country", "generated_at"}.issubset(df.columns):
            chart_data = df.pivot_table(index="generated_at", columns="country", values="score_total", aggfunc="mean")
            st.line_chart(chart_data)
        else:
            st.info("No hay datos suficientes para mostrar esta evolucion.")

    with tab_avg:
        st.markdown("### Desglose por dimensiones")
        if all(col in df.columns for col in DIMENSIONES_DASHBOARD):
            avg_dims = df.groupby("country")[DIMENSIONES_DASHBOARD].mean().T
            st.bar_chart(avg_dims)
        else:
            st.info("Faltan datos dimensionales en algunos registros.")

    with tab_src:
        st.markdown("### Calidad de la informacion recuperada")
        if "num_sources" in df.columns:
            st.bar_chart(df.groupby("country")["num_sources"].sum())
        else:
            st.warning("No se encontro la metrica de fuentes en el historial.")

    with tab_vol:
        st.markdown("### Estabilidad historica")
        volatilidad = compute_dispersion_scores(rows)
        st.dataframe(pd.DataFrame(volatilidad), use_container_width=True, hide_index=True)

    with tab_mean:
        st.markdown("### Posicion media historica")
        ranking_medio = compute_ranking_medio_por_pais(rows)
        st.table(pd.DataFrame(ranking_medio))


def mostrar_panel_configuracion() -> None:
    """Muestra la configuracion activa en la barra lateral."""
    with st.sidebar.expander("Configuracion activa", expanded=False):
        modo_label = "Demo (sin APIs)" if APP_MODE == "demo" else "Produccion (APIs reales)"
        color_modo = "🟡" if APP_MODE == "demo" else "🟢"
        st.markdown(f"**Modo:** {color_modo} {modo_label}")
        if APP_MODE == "demo":
            st.caption("Modo demo: solo usa datos precalculados del catálogo interno.")
            st.caption(f"Países demo soportados: {_get_demo_catalog_text()}")

        st.markdown("---")
        st.markdown("**Pesos por dimension** *(desde weights.yaml)*")
        pesos_df = pd.DataFrame(
            [{"Dimension": k.replace("_", " ").capitalize(), "Peso": f"{v:.0%}"} for k, v in SCORING_WEIGHTS.items()]
        )
        st.dataframe(pesos_df, use_container_width=True, hide_index=True)

        st.markdown("**Pais vs. sector**")
        st.caption(
            f"Pais: {COUNTRY_VS_SECTOR_WEIGHTS['score_riesgo_pais']:.0%} · "
            f"Sector: {COUNTRY_VS_SECTOR_WEIGHTS['score_riesgo_sectorial']:.0%}"
        )
        st.caption("Para cambiar los pesos, edita `config/weights.yaml` y reinicia la app.")


def inicializar_estado_sesion() -> None:
    """Inicializa y sanea el estado de sesion de la app."""
    claves = ["resultado_a", "resultado_b", "ranking_resultados", "p_a", "p_b"]
    for clave in claves:
        if clave not in st.session_state:
            st.session_state[clave] = None

    for clave in claves:
        valor = st.session_state.get(clave)
        if valor is not None:
            if clave == "ranking_resultados" and not isinstance(valor, list):
                st.session_state[clave] = None
            elif clave in ["resultado_a", "resultado_b"] and not isinstance(valor, dict):
                st.session_state[clave] = None
            elif clave in ["p_a", "p_b"] and not isinstance(valor, str):
                st.session_state[clave] = None


def main() -> None:
    st.set_page_config(
        page_title="P01 · Inteligencia comercial internacional",
        layout="wide",
        page_icon="🌍",
        initial_sidebar_state="expanded",
    )

    lang = st.sidebar.radio("Language / Idioma", ["es", "en"], horizontal=True)
    st.title(f"🌍 {get_text('title', lang=lang)}")
    st.caption(
        "Base publica actual del agente final de inteligencia comercial internacional. "
        "Esta version ayuda a comparar mercados y estructurar senales orientativas para decisiones comerciales."
    )
    st.info(
        "Los resultados son orientativos y se apoyan en busqueda web y analisis asistido por modelo. "
        "El indice orientativo de riesgo usa una escala 1-10 donde menor score implica mejor posicion relativa. "
        "No equivale a un rating certificado ni sustituye due diligence, asesoria juridica o analisis profesional."
    )

    inicializar_estado_sesion()
    menu_opciones = [
        get_text("menu_compare", lang=lang),
        get_text("menu_ranking", lang=lang),
        get_text("menu_dashboard", lang=lang),
    ]
    modo = st.sidebar.selectbox(get_text("sidebar_mode", lang=lang), menu_opciones)

    mostrar_panel_configuracion()

    if modo == get_text("menu_compare", lang=lang):
        modo_comparacion(lang)
    elif modo == get_text("menu_ranking", lang=lang):
        modo_ranking(lang)
    elif modo == get_text("menu_dashboard", lang=lang):
        mostrar_dashboard_panel(lang)

    st.sidebar.markdown("---")
    modo_str = "DEMO" if APP_MODE == "demo" else ("DEBUG" if DEBUG_MODE else "PROD")
    st.sidebar.caption(f"P01 · Inteligencia comercial internacional · Modo: {modo_str}")

    if st.sidebar.button(get_text("btn_clear_cache", lang=lang)):
        clear_country_analysis_cache()
        st.sidebar.success(get_text("cache_cleared_msg", lang=lang))
        time.sleep(1)
        st.rerun()


if __name__ == "__main__":
    main()
