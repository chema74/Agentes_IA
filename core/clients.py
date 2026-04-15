"""
clients.py

Responsabilidad:
crear y devolver los clientes externos del sistema.
"""

from __future__ import annotations

from typing import Tuple

from groq import Groq
from tavily import TavilyClient

from config.settings import (
    ENABLE_LLM_FALLBACK,
    FALLBACK_MODEL_NAME,
    GROQ_API_KEY,
    MODEL_NAME,
    REQUEST_TIMEOUT_SECONDS,
    TAVILY_API_KEY,
)


class ClientInitializationError(RuntimeError):
    """Error al inicializar clientes externos."""


def get_clients() -> Tuple[TavilyClient, Groq]:
    """
    Crea y devuelve los clientes de Tavily y Groq.

    Nota importante:
    muchos errores reales de red, timeout, SSL o autenticación
    pueden aparecer no aquí, sino en la primera llamada efectiva
    al proveedor.
    """
    if not TAVILY_API_KEY:
        raise ClientInitializationError("TAVILY_API_KEY no configurada.")
    if not GROQ_API_KEY:
        raise ClientInitializationError("GROQ_API_KEY no configurada.")

    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception as exc:
        raise ClientInitializationError(
            f"No se pudo inicializar TavilyClient: {exc}"
        ) from exc

    try:
        groq = Groq(
            api_key=GROQ_API_KEY,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except TypeError:
        # Compatibilidad con versiones antiguas del SDK de Groq
        # que no acepten 'timeout' en el constructor.
        try:
            groq = Groq(api_key=GROQ_API_KEY)
        except Exception as exc:
            raise ClientInitializationError(
                f"No se pudo inicializar Groq: {exc}"
            ) from exc
    except Exception as exc:
        raise ClientInitializationError(
            f"No se pudo inicializar Groq: {exc}"
        ) from exc

    return tavily, groq


def get_llm_models() -> list[str]:
    """
    Devuelve la lista ordenada de modelos a intentar.
    """
    models = [MODEL_NAME]

    if (
        ENABLE_LLM_FALLBACK
        and FALLBACK_MODEL_NAME
        and FALLBACK_MODEL_NAME != MODEL_NAME
    ):
        models.append(FALLBACK_MODEL_NAME)

    return models
