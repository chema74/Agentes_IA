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
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.clients import get_clients
from infrastructure.retry import with_retry
from domain.search import buscar_info
from domain.analysis import analizar_pais
from domain.parser import clean_json
from domain.scoring import calcular_scores
from domain.i18n import get_text
from domain.demo_data import get_demo_result, PAISES_DEMO
from domain.dashboard import (
    build_dashboard_rows,
    DIMENSIONES_DASHBOARD,
    compute_ranking_medio_por_pais,
    compute_dispersion_scores,
)
from domain.cache import (
    load_country_analysis_from_cache,
    save_country_analysis_to_cache,
    clear_country_analysis_cache,
)
from domain.logger import log_event
from domain.validators import (
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
)


def validar_configuracion_api() -> None:
    """Valida las claves necesarias segun el modo activo."""
    faltantes = []
    if not os.getenv("GROQ_API_KEY", "").strip():
        faltantes.append("GROQ_API_KEY")
    if APP_MODE == "production" and not os.getenv("TAVILY_API_KEY", "").strip():
        faltantes.append("TAVILY_API_KEY")

    if faltantes:
        raise RuntimeError(
            "Faltan claves de entorno: "
            + ", ".join(faltantes)
            + ". Copia .env.example a .env y anade las credenciales necesarias."
        )


def calcular_score_total(resultado: Dict[str, Any]) -> float:
    """Calcula un indice orientativo de oportunidad para comparar mercados."""
    scores = resultado.get("scores", {})
    if not scores:
        return 0.0

    valid_v = [v for v in scores.values() if isinstance(v, (int, float))]
    if not valid_v:
        return 0.0

    return sum(11 - v for v in valid_v) / len(valid_v)


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
                "justificacion_scores": scoring.get("justificacion_scores", {}),
                "fuentes": fuentes,
                "sector": sector,
                "tipo_empresa": tipo_empresa,
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
        st.info("Modo demo: datos precalculados sin llamadas a APIs.")
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
            "no como rating formal de riesgo pais."
        )


def modo_comparacion(lang: str) -> None:
    """Comparacion entre dos mercados."""
    st.subheader(get_text("menu_compare", lang=lang))

    with st.expander(get_text("compare_config_title", lang=lang), expanded=True):
        c1, c2 = st.columns(2)

        if APP_MODE == "demo":
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
                st.error(
                    f"No se pudo completar el analisis de {p_a}. Revisa el pais, el sector o las claves API y vuelve a intentarlo."
                )
            if not res_b:
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
            "No sustituye due diligence comercial, regulatoria o juridica."
        )

        score_a = calcular_score_total(st.session_state.resultado_a)
        score_b = calcular_score_total(st.session_state.resultado_b)
        col_v1, col_v2 = st.columns(2)
        col_v1.metric(st.session_state.p_a, f"{score_a:.1f}/10", delta=f"{score_a - score_b:+.1f}" if score_b != 0 else None, delta_color="off" if score_a > score_b else "inverse")
        col_v2.metric(st.session_state.p_b, f"{score_b:.1f}/10", delta=f"{score_b - score_a:+.1f}" if score_a != 0 else None, delta_color="off" if score_b > score_a else "inverse")


def modo_ranking(lang: str) -> None:
    """Genera una priorizacion orientativa de varios paises."""
    st.subheader(get_text("menu_ranking", lang=lang))
    st.caption(
        "Este ranking es una ayuda para priorizar mercados de forma comparativa. "
        "No equivale a un rating formal ni a una evaluacion exhaustiva de entrada a pais."
    )

    with st.expander("Configuracion del ranking", expanded=True):
        countries_input = st.text_area("Introduce paises (uno por linea)", value="Espana\nFrancia\nAlemania", height=100)
        sectores = get_text("sectors", section="domain", lang=lang)
        sector_sel = st.selectbox("Sector", sectores)
        tipos = get_text("company_types", section="domain", lang=lang)
        tipo_sel = st.selectbox("Tipo de empresa", tipos)

        if st.button("Generar ranking", use_container_width=True):
            countries = [c.strip() for c in countries_input.split("\n") if c.strip()]
            if len(countries) < 2:
                st.error("Introduce al menos dos paises para poder compararlos.")
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
                for i, pais in enumerate(countries):
                    resultado = construir_resultado_pais(tavily, groq, pais, sector_sel, tipo_sel, lang, force_refresh=False)
                    if resultado:
                        resultados.append({"pais": pais, "score": calcular_score_total(resultado), "resultado": resultado})
                    if APP_MODE == "production" and THROTTLING_DELAY > 0 and i < len(countries) - 1:
                        time.sleep(THROTTLING_DELAY)

            if resultados:
                resultados_ordenados = sorted(resultados, key=lambda x: x["score"], reverse=True)
                st.session_state.ranking_resultados = resultados_ordenados
                df_ranking = pd.DataFrame(
                    [
                        {"Posicion": i + 1, "Pais": r["pais"], "Indice orientativo": f"{r['score']:.2f}/10"}
                        for i, r in enumerate(resultados_ordenados)
                    ]
                )
                st.dataframe(df_ranking, use_container_width=True, hide_index=True)
                st.success(f"Ranking generado con {len(resultados_ordenados)} paises.")
            else:
                st.error("No se pudo completar el analisis de los paises indicados.")


def mostrar_dashboard_panel(lang: str) -> None:
    """Panel historico con metricas agregadas."""
    st.subheader(get_text("menu_dashboard", lang=lang))
    st.caption(
        "Panel historico para revisar resultados previos guardados por la aplicacion. "
        "Usalo como apoyo analitico interno, no como cuadro formal de riesgo pais."
    )

    try:
        rows = build_dashboard_rows()
    except Exception as exc:
        st.error(f"No se pudo cargar el historial de analisis: {exc}")
        if DEBUG_MODE:
            st.exception(exc)
        return

    if not rows:
        st.warning(get_text("no_data_msg", lang=lang))
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
        st.markdown("### Evolucion del indice orientativo")
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
            st.caption(f"Paises disponibles: {', '.join(PAISES_DEMO[:4])} y mas.")

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
        "No equivalen a un rating formal, una due diligence completa ni asesoria juridica o regulatoria."
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
