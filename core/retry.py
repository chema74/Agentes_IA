"""
retry.py

Responsabilidad:
envolver llamadas externas con una política uniforme de reintentos,
backoff exponencial y tratamiento especial de rate limits.
"""

from __future__ import annotations

import logging
import time
from typing import Callable, Type, TypeVar

from domain.errors import (
    ExternalServiceError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    RetryExhaustedError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Errores que NO deben reintentarse nunca
_NO_RETRY_ERRORS: tuple[Type[ExternalServiceError], ...] = (
    ProviderAuthenticationError,
)


def with_retry(
    fn: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 1.5,
    backoff_factor: float = 2.0,
    label: str = "operación",
) -> T:
    """
    Ejecuta fn con reintentos y backoff exponencial adaptativo.

    Reglas:
    - ProviderAuthenticationError: no se reintenta
    - ProviderRateLimitError: aplica pausa mínima de seguridad
    - ExternalServiceError: reintento normal con backoff
    - Otros errores: se relanzan tal cual
    """
    # Importación local para evitar posibles ciclos
    try:
        from config.settings import THROTTLING_DELAY as MIN_RATE_LIMIT_DELAY
    except ImportError:
        MIN_RATE_LIMIT_DELAY = 0.8

    if max_attempts < 1:
        raise ValueError("max_attempts debe ser >= 1")

    last_exc: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return fn()

        except _NO_RETRY_ERRORS:
            raise

        except ProviderRateLimitError as exc:
            last_exc = exc

            if attempt < max_attempts:
                calculated_backoff = base_delay * (backoff_factor ** (attempt - 1))
                delay = max(calculated_backoff, MIN_RATE_LIMIT_DELAY)

                logger.warning(
                    "[retry] %s — RATE LIMIT detectado en intento %d/%d. "
                    "Esperando %.1fs antes de reintentar.",
                    label,
                    attempt,
                    max_attempts,
                    delay,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "[retry] %s — Rate limit persistente tras %d intentos.",
                    label,
                    max_attempts,
                )

        except ExternalServiceError as exc:
            last_exc = exc

            if attempt < max_attempts:
                delay = base_delay * (backoff_factor ** (attempt - 1))

                logger.warning(
                    "[retry] %s — intento %d/%d fallido (%s). "
                    "Reintentando en %.1fs.",
                    label,
                    attempt,
                    max_attempts,
                    type(exc).__name__,
                    delay,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "[retry] %s — todos los intentos agotados (%d/%d).",
                    label,
                    attempt,
                    max_attempts,
                )

        except Exception:
            raise

    raise RetryExhaustedError(
        message=f"{label}: se agotaron {max_attempts} intentos.",
        attempts=max_attempts,
        original=last_exc,
    )
