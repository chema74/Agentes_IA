"""
demo_data.py

Fase 18 — Modo demo: datos precalculados para presentaciones y demos.

Propósito:
  En modo demo (APP_MODE=demo) la app no realiza llamadas reales a Groq ni
  a Tavily. En su lugar, devuelve respuestas precalculadas para un conjunto
  de países representativos. Esto permite:
    - Mostrar la app en presentaciones sin coste de API
    - Ejecutar demos offline
    - Acelerar la revisión del portfolio
    - Evitar errores de red en entornos sin credenciales

Uso:
  from domain.demo_data import get_demo_result, PAISES_DEMO
  resultado = get_demo_result("México", "Tecnología")

Autor: Txema Ríos — CC BY-SA 4.0
"""

from __future__ import annotations

import unicodedata
from typing import Any, Dict, List, Optional, Tuple

# -------------------------------------------------------------------
# 1. PAÍSES DISPONIBLES EN MODO DEMO
# -------------------------------------------------------------------
PAISES_DEMO = [
    "México",
    "Vietnam",
    "Marruecos",
    "Colombia",
    "Alemania",
    "India",
    "Brasil",
    "Australia",
]

# -------------------------------------------------------------------
# 2. PLANTILLA DE RESULTADO DEMO
#    Cada país tiene scores realistas basados en datos públicos de 2024.
#    Los valores siguen la escala 1–10 (1 = bajo riesgo, 10 = crítico).
# -------------------------------------------------------------------
_DEMO_SCORES: Dict[str, Dict[str, float]] = {
    "México": {
        "riesgo_politico":       5.5,
        "estabilidad_economica": 5.0,
        "riesgo_regulatorio":    4.5,
        "riesgo_comercial":      4.0,
        "riesgo_geopolitico":    4.0,
        "riesgo_operativo":      5.0,
        "ajuste_sectorial":      5.5,
        "oportunidad_sectorial": 4.5,
    },
    "Vietnam": {
        "riesgo_politico":       4.5,
        "estabilidad_economica": 3.5,
        "riesgo_regulatorio":    5.0,
        "riesgo_comercial":      4.0,
        "riesgo_geopolitico":    4.5,
        "riesgo_operativo":      4.5,
        "ajuste_sectorial":      4.0,
        "oportunidad_sectorial": 3.0,
    },
    "Marruecos": {
        "riesgo_politico":       4.0,
        "estabilidad_economica": 5.0,
        "riesgo_regulatorio":    4.5,
        "riesgo_comercial":      4.5,
        "riesgo_geopolitico":    4.0,
        "riesgo_operativo":      5.5,
        "ajuste_sectorial":      4.0,
        "oportunidad_sectorial": 4.0,
    },
    "Colombia": {
        "riesgo_politico":       5.0,
        "estabilidad_economica": 5.5,
        "riesgo_regulatorio":    5.0,
        "riesgo_comercial":      5.0,
        "riesgo_geopolitico":    5.0,
        "riesgo_operativo":      5.5,
        "ajuste_sectorial":      5.0,
        "oportunidad_sectorial": 5.0,
    },
    "Alemania": {
        "riesgo_politico":       2.0,
        "estabilidad_economica": 3.0,
        "riesgo_regulatorio":    3.0,
        "riesgo_comercial":      3.0,
        "riesgo_geopolitico":    3.5,
        "riesgo_operativo":      2.5,
        "ajuste_sectorial":      3.0,
        "oportunidad_sectorial": 4.0,
    },
    "India": {
        "riesgo_politico":       4.5,
        "estabilidad_economica": 4.0,
        "riesgo_regulatorio":    5.5,
        "riesgo_comercial":      5.0,
        "riesgo_geopolitico":    5.0,
        "riesgo_operativo":      5.5,
        "ajuste_sectorial":      4.0,
        "oportunidad_sectorial": 3.0,
    },
    "Brasil": {
        "riesgo_politico":       5.5,
        "estabilidad_economica": 5.5,
        "riesgo_regulatorio":    6.0,
        "riesgo_comercial":      5.5,
        "riesgo_geopolitico":    4.5,
        "riesgo_operativo":      6.0,
        "ajuste_sectorial":      5.0,
        "oportunidad_sectorial": 4.5,
    },
    "Australia": {
        "riesgo_politico":       1.5,
        "estabilidad_economica": 2.5,
        "riesgo_regulatorio":    2.5,
        "riesgo_comercial":      2.5,
        "riesgo_geopolitico":    3.0,
        "riesgo_operativo":      2.0,
        "ajuste_sectorial":      3.0,
        "oportunidad_sectorial": 3.5,
    },
}

_DEMO_RESUMENES: Dict[str, str] = {
    "México": (
        "México ofrece un mercado de acceso consolidado gracias al T-MEC, con una "
        "clase media en expansión y creciente adopción tecnológica. Los principales "
        "riesgos son la inseguridad jurídica en ciertos sectores y la volatilidad "
        "cambiaria del peso. La proximidad con EE.UU. actúa como factor estabilizador "
        "para cadenas de suministro orientadas al nearshoring."
    ),
    "Vietnam": (
        "Vietnam mantiene un crecimiento económico sólido (>6% anual) impulsado por "
        "manufactura y exportaciones. El marco regulatorio es complejo pero manejable "
        "para empresas con socios locales. La estabilidad política del partido único "
        "reduce la incertidumbre institucional a corto plazo."
    ),
    "Marruecos": (
        "Marruecos es la puerta de entrada natural al mercado africano para empresas "
        "europeas y españolas. El Acuerdo de Asociación con la UE facilita el comercio. "
        "La reforma regulatoria en curso mejora el clima de inversión, aunque la "
        "burocracia sigue siendo un obstáculo operativo relevante."
    ),
    "Colombia": (
        "Colombia presenta una economía diversificada con TLC activos con EE.UU. y la UE. "
        "La mejora de la seguridad en zonas urbanas ha dinamizado la inversión. "
        "Los riesgos principales son la incertidumbre regulatoria reciente y la "
        "persistente brecha de infraestructura en regiones interiores."
    ),
    "Alemania": (
        "Alemania es el mercado más grande de la UE, con infraestructura excelente y "
        "marco legal muy predecible. La competencia es intensa y los costes operativos "
        "son elevados. Las transiciones energética e industrial generan oportunidades "
        "para proveedores especializados, especialmente en tecnología y servicios B2B."
    ),
    "India": (
        "India es la economía de mayor crecimiento entre los mercados grandes (>7% PIB). "
        "La complejidad regulatoria y la fragmentación del mercado por estados requieren "
        "estrategia de entrada muy localizada. La clase media emergente ofrece "
        "oportunidades de largo plazo en consumo y servicios digitales."
    ),
    "Brasil": (
        "Brasil es el mayor mercado de América Latina con una base industrial diversa. "
        "La carga fiscal y burocrática es la más alta de la región (efecto 'Custo Brasil'). "
        "La devaluación del real y la complejidad aduanera elevan el riesgo operativo "
        "para exportadores sin presencia local establecida."
    ),
    "Australia": (
        "Australia combina estabilidad institucional anglosajona con una posición "
        "estratégica en el Indo-Pacífico. El mercado es sofisticado y exigente en "
        "calidad. Los TLC con China, Japón y Corea del Sur amplifican las "
        "oportunidades para distribuidores que usen Australia como hub regional."
    ),
}

_DEMO_ALERTAS: Dict[str, list] = {
    "México":     ["Riesgo de cambio regulatorio sectorial", "Volatilidad cambiaria moderada"],
    "Vietnam":    ["Restricciones a la propiedad extranjera en algunos sectores"],
    "Marruecos":  ["Burocracia aduanera", "Dependencia de lluvias en sector agrícola"],
    "Colombia":   ["Incertidumbre en política fiscal", "Infraestructura de transporte limitada"],
    "Alemania":   ["Alta competencia local establecida", "Costes laborales elevados"],
    "India":      ["Fragmentación normativa por estados", "Plazos de pagos largos en sector público"],
    "Brasil":     ["Carga fiscal muy elevada (Custo Brasil)", "Tipo de cambio volátil"],
    "Australia":  ["Mercado pequeño en volumen absoluto", "Distancia logística desde Europa"],
}

_DEMO_OPORTUNIDADES: Dict[str, list] = {
    "México":     ["Nearshoring industrial", "Servicios tecnológicos", "Energías renovables"],
    "Vietnam":    ["Manufactura ligera", "Electrónica", "Turismo y hostelería"],
    "Marruecos":  ["Agroalimentación", "Turismo", "Energías renovables (solar)"],
    "Colombia":   ["Agroexportación", "Tecnología fintech", "Infraestructura"],
    "Alemania":   ["Software B2B", "Automoción sostenible", "Ingeniería de precisión"],
    "India":      ["Tecnología (IT outsourcing)", "Farmacéutico", "Energía solar"],
    "Brasil":     ["Agroindustria", "Fintech", "Infraestructura portuaria"],
    "Australia":  ["Minería sostenible", "Servicios educativos", "Agroalimentación premium"],
}


# -------------------------------------------------------------------
# 3. FUNCIÓN PRINCIPAL: OBTENER RESULTADO DEMO
# -------------------------------------------------------------------

def get_demo_result(
    pais: str,
    sector: str = "General",
    tipo_empresa: str = "PYME exportadora",
) -> Optional[Dict[str, Any]]:
    """
    Devuelve un resultado de análisis precalculado para el país indicado.

    Paso 1: Busca el país en el catálogo de demos (insensible a mayúsculas).
    Paso 2: Construye la estructura de resultado idéntica a la del pipeline real.
    Paso 3: Incluye marca '_demo_mode': True para que la UI pueda informar al usuario.

    Devuelve None si el país no está en el catálogo demo.
    """
    # Paso 1: normalizar nombre del país para búsqueda tolerante
    pais_normalizado = _normalizar_pais(pais)
    if pais_normalizado is None:
        return None

    scores = _DEMO_SCORES[pais_normalizado]

    # Paso 2: calcular scores agregados con los mismos pesos que settings.py
    from config.settings import (  # importación tardía para evitar ciclos
        SCORING_WEIGHTS,
        COUNTRY_SCORE_DIMENSIONS,
        SECTOR_SCORE_DIMENSIONS,
        COUNTRY_VS_SECTOR_WEIGHTS,
    )

    score_pais = round(
        sum(scores.get(d, 5.0) * SCORING_WEIGHTS.get(d, 0.0)
            for d in COUNTRY_SCORE_DIMENSIONS)
        / max(sum(SCORING_WEIGHTS.get(d, 0.0) for d in COUNTRY_SCORE_DIMENSIONS), 1e-9),
        2,
    )

    score_sectorial = round(
        sum(scores.get(d, 5.0) * SCORING_WEIGHTS.get(d, 0.0)
            for d in SECTOR_SCORE_DIMENSIONS)
        / max(sum(SCORING_WEIGHTS.get(d, 0.0) for d in SECTOR_SCORE_DIMENSIONS), 1e-9),
        2,
    )

    score_total = round(
        score_pais * COUNTRY_VS_SECTOR_WEIGHTS["score_riesgo_pais"]
        + score_sectorial * COUNTRY_VS_SECTOR_WEIGHTS["score_riesgo_sectorial"],
        2,
    )

    # Paso 3: construir estructura de resultado compatible con el pipeline real
    justificacion = {
        dim: [f"[DEMO] Score precalculado: {val:.1f}/10"]
        for dim, val in scores.items()
    }
    cobertura = {dim: 2 for dim in scores}
    bandas = {dim: "media" for dim in scores}

    return {
        "resumen_ejecutivo":   _DEMO_RESUMENES.get(pais_normalizado, "Resumen no disponible."),
        "alertas":             _DEMO_ALERTAS.get(pais_normalizado, []),
        "oportunidades":       _DEMO_OPORTUNIDADES.get(pais_normalizado, []),
        "scores":              scores,
        "scores_agregados": {
            "score_riesgo_pais":      score_pais,
            "score_riesgo_sectorial": score_sectorial,
            "score_total":            score_total,
        },
        "justificacion_scores": justificacion,
        "cobertura_evidencia":  cobertura,
        "bandas_confianza":     bandas,
        "fuentes":              [],
        "sector":               sector,
        "tipo_empresa":         tipo_empresa,
        "_cache_used":          False,
        "_demo_mode":           True,
        "_scoring_fallback":    False,
    }


# -------------------------------------------------------------------
# 4. UTILIDAD: NORMALIZACIÓN DE NOMBRE DE PAÍS
# -------------------------------------------------------------------

def _normalizar_pais(pais: str) -> Optional[str]:
    """
    Busca el país en el catálogo de demos de forma insensible
    a mayúsculas y tildes básicas.
    Devuelve el nombre canónico o None si no se encuentra.
    """
    pais_lower = "".join(
        ch for ch in unicodedata.normalize("NFKD", pais.strip().lower())
        if not unicodedata.combining(ch)
    )
    for nombre_canon in _DEMO_SCORES:
        nombre_normalizado = "".join(
            ch for ch in unicodedata.normalize("NFKD", nombre_canon.lower())
            if not unicodedata.combining(ch)
        )
        if nombre_normalizado == pais_lower:
            return nombre_canon
    return None


def get_demo_supported_countries() -> List[str]:
    """
    Devuelve el catálogo oficial de países disponibles en modo demo.

    Paso 1: expone una única fuente de verdad para la UI.
    Paso 2: evita duplicar o reconstruir el catálogo en la app.
    """
    return list(PAISES_DEMO)


def split_demo_supported_countries(paises: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separa países soportados y no soportados por el catálogo demo.

    Paso 1: normaliza países soportados para usar el nombre canónico.
    Paso 2: conserva el texto introducido en los no soportados para mensajes claros.
    """
    soportados: List[str] = []
    no_soportados: List[str] = []

    for pais in paises:
        pais_limpio = str(pais).strip()
        if not pais_limpio:
            continue

        pais_canonico = _normalizar_pais(pais_limpio)
        if pais_canonico is None:
            no_soportados.append(pais_limpio)
        else:
            soportados.append(pais_canonico)

    return soportados, no_soportados


def pais_disponible_en_demo(pais: str) -> bool:
    """
    Comprueba si el país tiene datos demo disponibles.
    Útil para que la UI pueda informar al usuario antes del análisis.
    """
    return _normalizar_pais(pais) is not None
