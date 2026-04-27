"""
domain/i18n.py
Responsabilidad: Diccionario central de traducciones.
[FIX]: Añadida la clave 'compare_config_title' para evitar el texto entre corchetes.
"""

from __future__ import annotations
from typing import Dict, Any

I18N_DATA: Dict[str, Dict[str, Any]] = {
    "es": {
        "ui": {
            "title": "Inteligencia Comercial Internacional",
            "sidebar_mode": "Modo de análisis",
            "menu_compare": "Comparación",
            "menu_ranking": "Ranking",
            "menu_dashboard": "Dashboard",
            "menu_logs": "Logs",
            "compare_config_title": "Configuración de Comparación", # <--- ESTA ES LA PIEZA CLAVE
            "btn_compare": "Comparar países",
            "btn_ranking": "Generar Ranking",
            "country_label": "País",
            "sector_label": "Sector",
            "company_type_label": "Tipo de empresa",
            "ranking_input_help": "Países (separados por coma)",
            "analyzing_msg": "Analizando mercados...",
            "cache_hit_msg": "Resultado cargado desde caché local.",
            "summary_title": "Resumen ejecutivo",
            "scores_title": "Scores por dimensión",
            "dashboard_title": "Panel de Análisis Histórico",
            "no_data_msg": "No hay datos históricos disponibles.",
            "tab_evolution": "Evolución",
            "tab_average": "Promedios",
            "tab_sources": "Fuentes",
            "tab_volatility": "Volatilidad",
            "tab_ranking_medio": "Ranking Medio",
            "btn_clear_cache": "Vaciar Caché",
            "cache_cleared_msg": "Caché vaciada correctamente.",
            "err_retry_fail": "❌ Error crítico tras reintentos",
        },
        "domain": {
            "sectors": ["General", "Tecnología", "Agroalimentario", "Industrial", "Energía", "Logística", "Retail"],
            "company_types": ["PYME", "Gran Empresa", "Startup", "Autónomo", "Cooperativa"]
        }
    },
    "en": {
        "ui": {
            "title": "International Commercial Intelligence",
            "sidebar_mode": "Analysis Mode",
            "menu_compare": "Comparison",
            "menu_ranking": "Ranking",
            "menu_dashboard": "Dashboard",
            "menu_logs": "Logs",
            "compare_config_title": "Comparison Settings", # <--- Y AQUÍ PARA INGLÉS
            "btn_compare": "Compare Countries",
            "btn_ranking": "Generate Ranking",
            "country_label": "Country",
            "sector_label": "Sector",
            "company_type_label": "Company Type",
            "ranking_input_help": "Countries (comma separated)",
            "analyzing_msg": "Analyzing markets...",
            "cache_hit_msg": "Result loaded from local cache.",
            "summary_title": "Executive Summary",
            "scores_title": "Dimension Scores",
            "dashboard_title": "Historical Analysis Dashboard",
            "no_data_msg": "No historical data available.",
            "tab_evolution": "Evolution",
            "tab_average": "Averages",
            "tab_sources": "Sources",
            "tab_volatility": "Volatility",
            "tab_ranking_medio": "Mean Ranking",
            "btn_clear_cache": "Clear Cache",
            "cache_cleared_msg": "Cache cleared successfully.",
            "err_retry_fail": "❌ Critical error after retries",
        },
        "domain": {
            "sectors": ["General", "Technology", "Agrifood", "Industrial", "Energy", "Logistics", "Retail"],
            "company_types": ["SME", "Large Corporation", "Startup", "Freelance", "Cooperative"]
        }
    }
}

def get_text(key: str, section: str = "ui", lang: str = "es") -> Any:
    """Recupera un texto o lista del diccionario según el idioma seleccionado."""
    lang_dict = I18N_DATA.get(lang, I18N_DATA["es"])
    section_dict = lang_dict.get(section, lang_dict.get("ui", {}))
    return section_dict.get(key, f"[{key}]")