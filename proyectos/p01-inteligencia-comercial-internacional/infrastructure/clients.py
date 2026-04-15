"""
Clientes externos para P01.

Responsabilidad:
- inicializar clientes de Tavily y Groq con configuración centralizada
- fallar con mensajes claros cuando faltan claves
"""

from __future__ import annotations

from typing import Tuple

from groq import Groq
from tavily import TavilyClient

from config.settings import GROQ_API_KEY, REQUEST_TIMEOUT_SECONDS, TAVILY_API_KEY


class ClientInitializationError(RuntimeError):
    """Error al inicializar clientes externos."""


def get_clients() -> Tuple[TavilyClient, Groq]:
    """Crea y devuelve clientes listos para usar en la app."""
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
        groq = Groq(api_key=GROQ_API_KEY, timeout=REQUEST_TIMEOUT_SECONDS)
    except TypeError:
        # Compatibilidad con SDKs que no acepten timeout.
        groq = Groq(api_key=GROQ_API_KEY)
    except Exception as exc:
        raise ClientInitializationError(f"No se pudo inicializar Groq: {exc}") from exc

    return tavily, groq

