"""
analysis.py

Responsabilidad:
usar el modelo LLM para generar la parte narrativa del informe final
a partir de un contexto estructurado.

En Fase 10A añadimos:
- manejo robusto de errores del proveedor
- fallback de modelo
- degradación limpia ante fallos de Groq

En Fase 10C añadimos:
- logging técnico de llamadas al proveedor
- trazabilidad de modelo usado
- registro de errores y fallback

MEJORAS ADICIONALES DE ESTA VERSIÓN:
- acceso seguro al contexto para evitar KeyError
- tipado algo más preciso en metadata
- saneado básico de textos antes de construir el prompt
"""

from __future__ import annotations

from typing import Any, Dict, List

from groq import Groq
from groq import AuthenticationError, RateLimitError, APIConnectionError, APIStatusError

from config.settings import (
    MODEL_NAME,
    FALLBACK_MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
    ENABLE_LLM_FALLBACK,
)
from domain.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderResponseError,
)
from domain.logger import log_event
from domain.schemas import get_narrative_json_contract


def _get_models_to_try() -> List[str]:
    """
    Devuelve la lista ordenada de modelos a intentar.
    """
    models = [MODEL_NAME]

    if ENABLE_LLM_FALLBACK and FALLBACK_MODEL_NAME and FALLBACK_MODEL_NAME != MODEL_NAME:
        models.append(FALLBACK_MODEL_NAME)

    return models


def _safe_context_value(contexto: Dict[str, str], clave: str) -> str:
    """
    Obtiene una dimensión del contexto sin romper por KeyError.
    """
    valor = contexto.get(clave, "")
    texto = str(valor).strip() if valor is not None else ""
    return texto if texto else "No disponible."


def _ejecutar_llm_con_fallback(
    groq: Groq,
    prompt: str,
    max_tokens: int,
    operation_name: str,
    metadata: Dict[str, Any] | None = None,
) -> str:
    """
    Ejecuta una llamada robusta al LLM usando modelo principal
    y, si procede, modelo fallback.

    Lanza excepciones de dominio limpias para que la app pueda
    degradar sin romperse.
    """
    models_to_try = _get_models_to_try()
    last_error = None
    metadata = metadata or {}

    log_event(
        "llm_call_started",
        {
            "operation_name": operation_name,
            "models_to_try": models_to_try,
            "max_tokens": max_tokens,
            **metadata,
        },
    )

    for attempt_index, model_name in enumerate(models_to_try, start=1):
        try:
            log_event(
                "llm_model_attempt",
                {
                    "operation_name": operation_name,
                    "model_name": model_name,
                    "attempt_index": attempt_index,
                    **metadata,
                },
            )

            response = groq.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
                max_tokens=max_tokens,
            )

            if not response.choices:
                raise ProviderResponseError(
                    f"El modelo {model_name} devolvió una respuesta sin choices."
                )

            content = response.choices[0].message.content

            if not content or not content.strip():
                raise ProviderResponseError(
                    f"El modelo {model_name} devolvió contenido vacío."
                )

            log_event(
                "llm_call_succeeded",
                {
                    "operation_name": operation_name,
                    "model_name": model_name,
                    "attempt_index": attempt_index,
                    "used_fallback": attempt_index > 1,
                    **metadata,
                },
            )

            return content

        except AuthenticationError as e:
            log_event(
                "llm_authentication_error",
                {
                    "operation_name": operation_name,
                    "model_name": model_name,
                    "error": str(e),
                    **metadata,
                },
            )
            raise ProviderAuthenticationError(
                f"Error de autenticación con Groq usando el modelo {model_name}: {e}"
            ) from e

        except RateLimitError as e:
            last_error = e
            log_event(
                "llm_rate_limit_error",
                {
                    "operation_name": operation_name,
                    "model_name": model_name,
                    "error": str(e),
                    **metadata,
                },
            )
            continue

        except APIConnectionError as e:
            last_error = e
            log_event(
                "llm_connection_error",
                {
                    "operation_name": operation_name,
                    "model_name": model_name,
                    "error": str(e),
                    **metadata,
                },
            )
            continue

        except APIStatusError as e:
            status_code = getattr(e, "status_code", None)

            log_event(
                "llm_api_status_error",
                {
                    "operation_name": operation_name,
                    "model_name": model_name,
                    "status_code": status_code,
                    "error": str(e),
                    **metadata,
                },
            )

            if status_code == 401:
                raise ProviderAuthenticationError(
                    f"Error de autenticación con Groq usando el modelo {model_name}: {e}"
                ) from e

            if status_code == 429:
                last_error = e
                continue

            last_error = e
            continue

        except ProviderResponseError as e:
            last_error = e
            log_event(
                "llm_response_error",
                {
                    "operation_name": operation_name,
                    "model_name": model_name,
                    "error": str(e),
                    **metadata,
                },
            )
            continue

        except Exception as e:
            last_error = e
            log_event(
                "llm_unexpected_error",
                {
                    "operation_name": operation_name,
                    "model_name": model_name,
                    "error": str(e),
                    **metadata,
                },
            )
            continue

    if last_error:
        error_text = str(last_error).lower()

        if "rate limit" in error_text or "429" in error_text or "limit" in error_text:
            raise ProviderRateLimitError(
                f"No fue posible obtener respuesta del LLM por límite de cuota o rate limit: {last_error}"
            ) from last_error

        if "timeout" in error_text or "timed out" in error_text:
            raise ProviderTimeoutError(
                f"Timeout al invocar el proveedor LLM: {last_error}"
            ) from last_error

        raise ProviderResponseError(
            f"Fallo al generar respuesta con los modelos configurados: {last_error}"
        ) from last_error

    raise ProviderResponseError("No fue posible obtener respuesta del LLM.")


def analizar_pais(
    groq: Groq,
    pais: str,
    sector: str,
    tipo: str,
    contexto: Dict[str, str],
) -> str:
    """
    Genera la parte narrativa del informe final en formato JSON textual.
    """
    contexto_politico = _safe_context_value(contexto, "politico")
    contexto_economico = _safe_context_value(contexto, "economico")
    contexto_regulatorio = _safe_context_value(contexto, "regulatorio")
    contexto_oportunidades = _safe_context_value(contexto, "oportunidades")

    prompt = f"""
Eres analista experto en riesgo país para exportación e internacionalización.

Debes analizar el país: {pais}
Sector objetivo: {sector}
Tipo de empresa: {tipo}

CONTEXTO POLÍTICO:
{contexto_politico}

CONTEXTO ECONÓMICO:
{contexto_economico}

CONTEXTO REGULATORIO:
{contexto_regulatorio}

OPORTUNIDADES DE MERCADO:
{contexto_oportunidades}

INSTRUCCIONES:
- Usa SOLO la información del contexto anterior
- No inventes hechos fuera del contexto
- Si falta información, sé prudente
- Elabora un análisis profesional, breve y claro
- Devuelve SOLO JSON válido, sin markdown, sin texto adicional
- NO incluyas scores numéricos
- El resumen debe ser útil para una decisión empresarial

El JSON debe tener exactamente esta estructura:

{get_narrative_json_contract()}

REGLAS:
- 'resumen_ejecutivo' debe tener entre 2 y 4 frases
- 'alertas' debe incluir exactamente 3 elementos
- 'oportunidades' debe incluir exactamente 3 elementos
- Las alertas deben reflejar riesgos relevantes del contexto
- Las oportunidades deben ser coherentes con el país y el sector

Responde SOLO con JSON válido.
"""

    return _ejecutar_llm_con_fallback(
        groq=groq,
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        operation_name="analizar_pais",
        metadata={
            "country": pais,
            "sector": sector,
            "company_type": tipo,
        },
    )


def comparar_paises(
    groq: Groq,
    pais_a: str,
    pais_b: str,
    resultado_a: Dict[str, Any],
    resultado_b: Dict[str, Any],
    sector: str,
    tipo: str,
) -> str:
    """
    Genera una comparación narrativa entre dos países
    usando resultados ya estructurados por el sistema.

    IMPORTANTE:
    Aquí el LLM no debe recalcular scores.
    Solo debe interpretar los resultados ya construidos.

    Devuelve texto libre, no JSON.
    """

    prompt = f"""
Eres analista experto en expansión internacional.

Debes comparar dos países para una decisión de entrada de mercado.

PAÍS A: {pais_a}
Resultado A:
{resultado_a}

PAÍS B: {pais_b}
Resultado B:
{resultado_b}

Sector objetivo: {sector}
Tipo de empresa: {tipo}

INSTRUCCIONES:
- Compara ambos países de forma clara y profesional
- Usa los resultados proporcionados
- No inventes datos fuera del contenido dado
- Evalúa:
  1. Riesgo político
  2. Riesgo comercial
  3. Estabilidad económica
  4. Oportunidades
- Termina con una recomendación comparativa:
  - cuál parece mejor candidato
  - en qué condiciones
  - con qué cautelas

FORMATO:
- Responde en español
- Máximo 250 palabras
- Texto claro, útil y ejecutivo
"""

    return _ejecutar_llm_con_fallback(
        groq=groq,
        prompt=prompt,
        max_tokens=600,
        operation_name="comparar_paises",
        metadata={
            "country_a": pais_a,
            "country_b": pais_b,
            "sector": sector,
            "company_type": tipo,
        },
    )
