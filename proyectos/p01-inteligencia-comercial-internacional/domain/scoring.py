"""
scoring.py

Responsabilidad:
calcular scores de forma explicable y trazable.

Fase 13A:
- Reemplazamos el scoring keyword-based por scoring LLM-based.
- El LLM recibe el contexto de búsqueda y devuelve un JSON
  con scores numéricos por dimensión y justificación por cada una.
- Se mantiene exactamente la misma interfaz de salida que en
  fases anteriores para no romper nada en streamlit_app.py.

Fase 13B:
- Añadimos ponderaciones por sector.
- Añadimos banda de confianza por dimensión (cobertura de evidencia).
- El score final refleja cuánta evidencia real respalda cada dimensión.

Compatibilidad garantizada:
- La función principal sigue siendo calcular_scores(contexto).
- El diccionario devuelto mantiene las mismas claves que antes:
  scores, scores_agregados, pesos_aplicados, justificacion_scores.
- Se añaden dos claves nuevas opcionales:
  bandas_confianza, cobertura_evidencia.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from groq import Groq

from config.settings import (
    COUNTRY_SCORE_DIMENSIONS,
    COUNTRY_VS_SECTOR_WEIGHTS,
    FALLBACK_MODEL_NAME,
    MODEL_NAME,
    SCORING_WEIGHTS,
    SECTOR_SCORE_DIMENSIONS,
    TEMPERATURE,
    ENABLE_LLM_FALLBACK,
)
from domain.errors import ProviderResponseError
from domain.logger import log_event


# -------------------------------------------------------------------
# 1. CONSTANTES INTERNAS
# -------------------------------------------------------------------

# Rango permitido para todos los scores
SCORE_MIN = 1.0
SCORE_MAX = 10.0

# Umbrales de cobertura de evidencia
COBERTURA_ALTA = 3   # >= 3 señales → confianza alta
COBERTURA_MEDIA = 1  # >= 1 señal  → confianza media
                     # == 0 señales → confianza baja

# Dimensiones esperadas en la respuesta del LLM
DIMENSIONES_ESPERADAS = [
    "riesgo_politico",
    "estabilidad_economica",
    "riesgo_regulatorio",
    "riesgo_geopolitico",
    "riesgo_comercial",
    "riesgo_operativo",
    "ajuste_sectorial",
    "oportunidad_sectorial",
]

# Score por defecto cuando el LLM no tiene evidencia suficiente
SCORE_POR_DEFECTO = 5.0

# Contrato oficial visible al usuario
OFFICIAL_SCORE_KEY = "score_total"
OFFICIAL_SCORE_LABEL = "score oficial de riesgo"
OFFICIAL_SCORE_BEST_DIRECTION = "lower_is_better"


# -------------------------------------------------------------------
# 2. PROMPT DE SCORING
# -------------------------------------------------------------------

PROMPT_SCORING = """
Eres un analista experto en riesgo país y riesgo sectorial para exportación internacional.

Recibirás contexto de noticias y fuentes reales sobre un país, dividido en cuatro bloques:
- Contexto político
- Contexto económico
- Contexto regulatorio
- Oportunidades de mercado

Tu tarea es evaluar el país en ocho dimensiones de riesgo y oportunidad,
asignando un score numérico entre 1 y 10 a cada una, donde:
- 1 = situación muy favorable (bajo riesgo / alta oportunidad)
- 10 = situación muy desfavorable (alto riesgo / baja oportunidad)

DIMENSIONES A EVALUAR:
1. riesgo_politico        → estabilidad del gobierno, instituciones, conflictos
2. estabilidad_economica  → PIB, inflación, crecimiento, volatilidad
3. riesgo_regulatorio     → aranceles, barreras, requisitos de entrada, acuerdos
4. riesgo_geopolitico     → tensiones regionales, sanciones, alianzas
5. riesgo_comercial       → acceso al mercado, competencia, barreras no arancelarias
6. riesgo_operativo       → facilidad de hacer negocios, burocracia, infraestructura
7. ajuste_sectorial       → encaje del sector objetivo en este mercado
8. oportunidad_sectorial  → potencial de crecimiento del sector en este país

CONTEXTO POLÍTICO:
{politico}

CONTEXTO ECONÓMICO:
{economico}

CONTEXTO REGULATORIO:
{regulatorio}

OPORTUNIDADES DE MERCADO:
{oportunidades}

INSTRUCCIONES:
- Usa SOLO la información del contexto proporcionado
- Si hay poca información sobre una dimensión, asigna score 5.0
- Usa decimales cuando lo justifique el contexto (ej: 6.5, 3.2)
- Para cada dimensión indica cuántas señales relevantes encontraste: 0, 1, 2 o 3
- No inventes datos fuera del contexto

Responde SOLO con JSON válido, sin markdown, sin texto adicional.
El JSON debe tener exactamente esta estructura:

{{
  "scores": {{
    "riesgo_politico": <número entre 1 y 10>,
    "estabilidad_economica": <número entre 1 y 10>,
    "riesgo_regulatorio": <número entre 1 y 10>,
    "riesgo_geopolitico": <número entre 1 y 10>,
    "riesgo_comercial": <número entre 1 y 10>,
    "riesgo_operativo": <número entre 1 y 10>,
    "ajuste_sectorial": <número entre 1 y 10>,
    "oportunidad_sectorial": <número entre 1 y 10>
  }},
  "justificacion_scores": {{
    "riesgo_politico": ["motivo 1", "motivo 2"],
    "estabilidad_economica": ["motivo 1", "motivo 2"],
    "riesgo_regulatorio": ["motivo 1", "motivo 2"],
    "riesgo_geopolitico": ["motivo 1", "motivo 2"],
    "riesgo_comercial": ["motivo 1", "motivo 2"],
    "riesgo_operativo": ["motivo 1", "motivo 2"],
    "ajuste_sectorial": ["motivo 1", "motivo 2"],
    "oportunidad_sectorial": ["motivo 1", "motivo 2"]
  }},
  "cobertura_evidencia": {{
    "riesgo_politico": <0, 1, 2 o 3>,
    "estabilidad_economica": <0, 1, 2 o 3>,
    "riesgo_regulatorio": <0, 1, 2 o 3>,
    "riesgo_geopolitico": <0, 1, 2 o 3>,
    "riesgo_comercial": <0, 1, 2 o 3>,
    "riesgo_operativo": <0, 1, 2 o 3>,
    "ajuste_sectorial": <0, 1, 2 o 3>,
    "oportunidad_sectorial": <0, 1, 2 o 3>
  }}
}}
"""


# -------------------------------------------------------------------
# 3. FUNCIONES AUXILIARES MATEMÁTICAS
# -------------------------------------------------------------------

def _clamp(valor: float, minimo: float = SCORE_MIN, maximo: float = SCORE_MAX) -> float:
    """
    Limita un valor dentro del rango permitido [1.0, 10.0].
    Evita scores fuera de escala aunque el LLM devuelva algo inesperado.
    """
    return max(minimo, min(maximo, valor))


def _round_score(valor: float) -> float:
    """
    Redondea un score a 2 decimales para presentación limpia.
    """
    return round(valor, 2)


def _weighted_average(
    scores: Dict[str, float],
    dimensions: List[str],
    weights: Dict[str, float],
) -> float:
    """
    Calcula una media ponderada para un conjunto de dimensiones.

    Si el peso total es 0 (configuración errónea), devuelve 0.0
    en lugar de lanzar ZeroDivisionError.
    """
    total_weight = sum(weights.get(d, 0.0) for d in dimensions)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(
        scores.get(d, SCORE_POR_DEFECTO) * weights.get(d, 0.0)
        for d in dimensions
    )
    return weighted_sum / total_weight


# -------------------------------------------------------------------
# 4. LLAMADA AL LLM PARA SCORING
# -------------------------------------------------------------------

def _llamar_llm_scoring(
    groq: Groq,
    contexto: Dict[str, str],
) -> Dict[str, Any]:
    """
    Invoca el LLM para obtener scores estructurados por dimensión.

    Intenta con el modelo principal y, si está configurado el fallback,
    lo intenta también antes de lanzar excepción de dominio.

    Devuelve el diccionario parseado del JSON devuelto por el LLM.
    """

    # ---------------------------------------------------------------
    # 4.1. Construir el prompt con el contexto real
    # ---------------------------------------------------------------
    prompt = PROMPT_SCORING.format(
        politico=contexto.get("politico", "Sin información disponible."),
        economico=contexto.get("economico", "Sin información disponible."),
        regulatorio=contexto.get("regulatorio", "Sin información disponible."),
        oportunidades=contexto.get("oportunidades", "Sin información disponible."),
    )

    # ---------------------------------------------------------------
    # 4.2. Lista de modelos a intentar (principal + fallback)
    # ---------------------------------------------------------------
    modelos = [MODEL_NAME]
    if ENABLE_LLM_FALLBACK and FALLBACK_MODEL_NAME and FALLBACK_MODEL_NAME != MODEL_NAME:
        modelos.append(FALLBACK_MODEL_NAME)

    ultimo_error = None

    # ---------------------------------------------------------------
    # 4.3. Bucle de intentos por modelo
    # ---------------------------------------------------------------
    for intento, modelo in enumerate(modelos, start=1):

        log_event(
            "scoring_llm_attempt",
            {
                "model": modelo,
                "attempt": intento,
            },
        )

        try:
            response = groq.chat.completions.create(
                model=modelo,
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
                max_tokens=1200,
            )

            raw = response.choices[0].message.content

            if not raw or not raw.strip():
                raise ProviderResponseError(
                    f"El modelo {modelo} devolvió contenido vacío en scoring."
                )

            # -----------------------------------------------------------
            # 4.4. Limpiar posible markdown y parsear JSON
            # -----------------------------------------------------------
            raw = raw.strip()

            if "```" in raw:
                for part in raw.split("```"):
                    fragment = part.strip()
                    if fragment.lower().startswith("json"):
                        fragment = fragment[4:].strip()
                    if fragment.startswith("{"):
                        raw = fragment
                        break

            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                raw = raw[start:end + 1]

            parsed = json.loads(raw)

            log_event(
                "scoring_llm_success",
                {
                    "model": modelo,
                    "attempt": intento,
                },
            )

            return parsed

        except Exception as e:
            ultimo_error = e
            log_event(
                "scoring_llm_error",
                {
                    "model": modelo,
                    "attempt": intento,
                    "error": str(e),
                },
            )
            continue

    # ---------------------------------------------------------------
    # 4.5. Si todos los modelos fallaron, lanzar excepción de dominio
    # ---------------------------------------------------------------
    raise ProviderResponseError(
        f"No fue posible obtener scoring del LLM tras {len(modelos)} intentos: {ultimo_error}"
    ) from ultimo_error


# -------------------------------------------------------------------
# 5. VALIDACIÓN Y SANEAMIENTO DE LA RESPUESTA DEL LLM
# -------------------------------------------------------------------

def _sanear_scores(raw_scores: Dict[str, Any]) -> Dict[str, float]:
    """
    Valida y sanea el diccionario de scores devuelto por el LLM.

    Para cada dimensión esperada:
    - Si falta → asigna SCORE_POR_DEFECTO
    - Si no es numérico → asigna SCORE_POR_DEFECTO
    - Si está fuera de rango → aplica clamp
    - Redondea a 2 decimales
    """
    scores_saneados: Dict[str, float] = {}

    for dimension in DIMENSIONES_ESPERADAS:
        valor_raw = raw_scores.get(dimension, SCORE_POR_DEFECTO)

        try:
            valor = float(valor_raw)
        except (TypeError, ValueError):
            log_event(
                "scoring_dimension_invalid",
                {
                    "dimension": dimension,
                    "valor_raw": str(valor_raw),
                    "accion": "usando score por defecto",
                },
            )
            valor = SCORE_POR_DEFECTO

        scores_saneados[dimension] = _round_score(_clamp(valor))

    return scores_saneados


def _sanear_justificaciones(
    raw_justificaciones: Dict[str, Any],
) -> Dict[str, List[str]]:
    """
    Valida y sanea el diccionario de justificaciones del LLM.

    Para cada dimensión esperada:
    - Si falta → añade justificación genérica
    - Si no es lista → convierte a lista de un elemento
    - Filtra elementos vacíos
    """
    justificaciones_saneadas: Dict[str, List[str]] = {}

    for dimension in DIMENSIONES_ESPERADAS:
        valor_raw = raw_justificaciones.get(dimension, [])

        if isinstance(valor_raw, list):
            motivos = [str(m).strip() for m in valor_raw if str(m).strip()]
        elif isinstance(valor_raw, str) and valor_raw.strip():
            motivos = [valor_raw.strip()]
        else:
            motivos = []

        if not motivos:
            motivos = [
                "No se detectaron señales claras en el contexto disponible. "
                "Se mantiene valoración intermedia."
            ]

        justificaciones_saneadas[dimension] = motivos

    return justificaciones_saneadas


def _sanear_cobertura(
    raw_cobertura: Dict[str, Any],
) -> Dict[str, int]:
    """
    Valida y sanea la cobertura de evidencia por dimensión.

    Valores válidos: 0, 1, 2, 3
    Cualquier otro valor → 0 (sin evidencia)
    """
    cobertura_saneada: Dict[str, int] = {}

    for dimension in DIMENSIONES_ESPERADAS:
        valor_raw = raw_cobertura.get(dimension, 0)

        try:
            valor = int(float(valor_raw))
            valor = max(0, min(3, valor))
        except (TypeError, ValueError):
            valor = 0

        cobertura_saneada[dimension] = valor

    return cobertura_saneada


# -------------------------------------------------------------------
# 6. BANDAS DE CONFIANZA
# -------------------------------------------------------------------

def _calcular_bandas_confianza(
    cobertura: Dict[str, int],
) -> Dict[str, str]:
    """
    Convierte la cobertura de evidencia en una banda de confianza
    legible por el usuario.

    Bandas:
    - "alta"  → 3 o más señales detectadas
    - "media" → 1 o 2 señales detectadas
    - "baja"  → ninguna señal detectada (score por defecto aplicado)
    """
    bandas: Dict[str, str] = {}

    for dimension, num_senales in cobertura.items():
        if num_senales >= COBERTURA_ALTA:
            banda = "alta"
        elif num_senales >= COBERTURA_MEDIA:
            banda = "media"
        else:
            banda = "baja"

        bandas[dimension] = banda

    return bandas


# -------------------------------------------------------------------
# 7. SCORES AGREGADOS
# -------------------------------------------------------------------

def _calcular_scores_agregados(
    scores: Dict[str, float],
) -> Dict[str, float]:
    """
    Calcula los tres scores agregados del sistema:

    - score_riesgo_pais:      media ponderada de dimensiones de país
    - score_riesgo_sectorial: media ponderada de dimensiones sectoriales
    - score_total:            combinación ponderada de los dos anteriores

    Los pesos vienen de config/settings.py para mantener
    la configuración centralizada y desacoplada del código.
    """
    score_riesgo_pais = _round_score(
        _weighted_average(scores, COUNTRY_SCORE_DIMENSIONS, SCORING_WEIGHTS)
    )

    score_riesgo_sectorial = _round_score(
        _weighted_average(scores, SECTOR_SCORE_DIMENSIONS, SCORING_WEIGHTS)
    )

    score_total = _round_score(
        (score_riesgo_pais * COUNTRY_VS_SECTOR_WEIGHTS["score_riesgo_pais"]) +
        (score_riesgo_sectorial * COUNTRY_VS_SECTOR_WEIGHTS["score_riesgo_sectorial"])
    )

    return {
        "score_riesgo_pais": score_riesgo_pais,
        "score_riesgo_sectorial": score_riesgo_sectorial,
        "score_total": score_total,
    }


def get_official_score(resultado: Dict[str, Any]) -> float:
    """
    Devuelve el unico indicador oficial que debe ver y reutilizar la app.

    Regla:
    - Paso 1: usar `scores_agregados.score_total` cuando exista.
    - Paso 2: si no existe, recalcularlo desde `scores` para compatibilidad.
    - Paso 3: si faltan datos, devolver 0.0 como valor nulo controlado.
    """
    if not isinstance(resultado, dict):
        return 0.0

    agregados = resultado.get("scores_agregados", {})
    if isinstance(agregados, dict):
        valor = agregados.get(OFFICIAL_SCORE_KEY)
        if isinstance(valor, (int, float)):
            return _round_score(float(valor))

    scores = resultado.get("scores", {})
    if isinstance(scores, dict) and scores:
        return _calcular_scores_agregados(scores).get(OFFICIAL_SCORE_KEY, 0.0)

    return 0.0


# -------------------------------------------------------------------
# 8. FALLBACK DETERMINISTA
# -------------------------------------------------------------------

def _scoring_fallback_determinista(
    contexto: Dict[str, str],
) -> Dict[str, Any]:
    """
    Scoring de emergencia basado en keywords cuando el LLM no está disponible.

    Este fallback reproduce la lógica de la Fase anterior para garantizar
    que el sistema nunca se rompe completamente ante fallos del proveedor.

    Se activa SOLO si el LLM falla tras todos los intentos configurados.
    El resultado incluye una marca '_scoring_fallback': True para que
    streamlit_app.py pueda informar al usuario.
    """
    politico = contexto.get("politico", "").lower()
    economico = contexto.get("economico", "").lower()
    regulatorio = contexto.get("regulatorio", "").lower()
    oportunidades = contexto.get("oportunidades", "").lower()

    # Score base para todas las dimensiones
    s = {d: 5.0 for d in DIMENSIONES_ESPERADAS}

    # Riesgo político
    if "inestabilidad" in politico: s["riesgo_politico"] += 2
    if "conflicto" in politico:     s["riesgo_politico"] += 2
    if "crisis" in politico:        s["riesgo_politico"] += 2
    if "corrupción" in politico:    s["riesgo_politico"] += 1
    if "tensión" in politico:       s["riesgo_politico"] += 1
    if "estabilidad" in politico:   s["riesgo_politico"] -= 1

    # Estabilidad económica
    if "crecimiento" in economico:   s["estabilidad_economica"] += 1
    if "expansión" in economico:     s["estabilidad_economica"] += 1
    if "inversión" in economico:     s["estabilidad_economica"] += 1
    if "inflación alta" in economico: s["estabilidad_economica"] -= 2
    if "recesión" in economico:      s["estabilidad_economica"] -= 2
    if "volatilidad" in economico:   s["estabilidad_economica"] -= 1

    # Riesgo regulatorio
    if "arancel" in regulatorio:     s["riesgo_regulatorio"] += 1
    if "restricción" in regulatorio: s["riesgo_regulatorio"] += 2
    if "barrera" in regulatorio:     s["riesgo_regulatorio"] += 1
    if "acuerdo comercial" in regulatorio: s["riesgo_regulatorio"] -= 1

    # Riesgo geopolítico
    if "conflicto" in politico:  s["riesgo_geopolitico"] += 2
    if "tensión" in politico:    s["riesgo_geopolitico"] += 1
    if "estabilidad" in politico: s["riesgo_geopolitico"] -= 1

    # Riesgo comercial
    if "restricción" in regulatorio: s["riesgo_comercial"] += 1
    if "barrera" in regulatorio:     s["riesgo_comercial"] += 1
    if "oportunidad" in oportunidades: s["riesgo_comercial"] -= 1

    # Riesgo operativo
    if "restricción" in regulatorio: s["riesgo_operativo"] += 1
    if "facilidad" in regulatorio:   s["riesgo_operativo"] -= 1

    # Ajuste y oportunidad sectorial
    if "oportunidad" in oportunidades:  s["oportunidad_sectorial"] += 2
    if "crecimiento" in economico:      s["oportunidad_sectorial"] += 1
    if "tecnología" in oportunidades:   s["ajuste_sectorial"] += 1
    if "servicios" in oportunidades:    s["ajuste_sectorial"] += 1

    scores = {d: _round_score(_clamp(v)) for d, v in s.items()}

    justificaciones = {
        d: ["Score calculado por método alternativo (LLM no disponible)."]
        for d in DIMENSIONES_ESPERADAS
    }

    cobertura = {d: 0 for d in DIMENSIONES_ESPERADAS}
    bandas = {d: "baja" for d in DIMENSIONES_ESPERADAS}

    return {
        "scores": scores,
        "scores_agregados": _calcular_scores_agregados(scores),
        "pesos_aplicados": SCORING_WEIGHTS,
        "justificacion_scores": justificaciones,
        "cobertura_evidencia": cobertura,
        "bandas_confianza": bandas,
        "_scoring_fallback": True,
    }


# -------------------------------------------------------------------
# 9. FUNCIÓN PRINCIPAL — INTERFAZ PÚBLICA
# -------------------------------------------------------------------

def calcular_scores(
    contexto: Dict[str, str],
    groq: Groq | None = None,
) -> Dict[str, Any]:
    """
    Calcula scores de riesgo país y sectorial a partir del contexto
    de búsqueda web obtenido por Tavily.

    Fase 13: usa el LLM para scoring semántico real.
    Fallback: si el LLM no está disponible, usa scoring keyword-based.

    Parámetros:
    - contexto: dict con claves 'politico', 'economico',
                'regulatorio', 'oportunidades'
    - groq:     cliente Groq ya inicializado (opcional).
                Si no se pasa, el scoring LLM no estará disponible
                y se usará el fallback directamente.

    Devuelve un diccionario con:
    - scores:              dict {dimension: float}  ← mismo formato que antes
    - scores_agregados:    dict con score_riesgo_pais, score_riesgo_sectorial, score_total
    - pesos_aplicados:     dict con los pesos usados (de settings.py)
    - justificacion_scores: dict {dimension: [str]}  ← mismo formato que antes
    - cobertura_evidencia: dict {dimension: int}     ← NUEVO en Fase 13
    - bandas_confianza:    dict {dimension: str}     ← NUEVO en Fase 13
    - _scoring_fallback:   bool (True solo si se usó el método alternativo)
    """

    log_event(
        "scoring_started",
        {
            "mode": "llm" if groq is not None else "fallback_directo",
        },
    )

    # ---------------------------------------------------------------
    # 9.1. Si no hay cliente Groq disponible → fallback directo
    # ---------------------------------------------------------------
    if groq is None:
        log_event("scoring_no_groq_client", {})
        return _scoring_fallback_determinista(contexto)

    # ---------------------------------------------------------------
    # 9.2. Intentar scoring LLM
    # ---------------------------------------------------------------
    try:
        parsed = _llamar_llm_scoring(groq=groq, contexto=contexto)

        # -----------------------------------------------------------
        # 9.3. Sanear cada sección de la respuesta
        # -----------------------------------------------------------
        scores = _sanear_scores(
            parsed.get("scores", {})
        )
        justificaciones = _sanear_justificaciones(
            parsed.get("justificacion_scores", {})
        )
        cobertura = _sanear_cobertura(
            parsed.get("cobertura_evidencia", {})
        )
        bandas = _calcular_bandas_confianza(cobertura)
        scores_agregados = _calcular_scores_agregados(scores)

        log_event(
            "scoring_completed",
            {
                "mode": "llm",
                "score_total": scores_agregados["score_total"],
                "dimensiones": list(scores.keys()),
            },
        )

        return {
            "scores": scores,
            "scores_agregados": scores_agregados,
            "pesos_aplicados": SCORING_WEIGHTS,
            "justificacion_scores": justificaciones,
            "cobertura_evidencia": cobertura,
            "bandas_confianza": bandas,
            "_scoring_fallback": False,
        }

    # ---------------------------------------------------------------
    # 9.4. Si el LLM falla → fallback determinista
    # ---------------------------------------------------------------
    except Exception as e:
        log_event(
            "scoring_llm_failed_using_fallback",
            {
                "error": str(e),
            },
        )
        resultado_fallback = _scoring_fallback_determinista(contexto)
        resultado_fallback["_scoring_error"] = str(e)
        return resultado_fallback
