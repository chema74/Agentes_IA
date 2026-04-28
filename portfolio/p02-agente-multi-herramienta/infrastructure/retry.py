"""
infrastructure/retry.py
-----------------------
Lgica de resiliencia para llamadas a APIs externas (Groq, Tavily).
Inspirado en la Fase 18B del proyecto p01.
"""

import time
import logging
from typing import Callable, TypeVar
from groq import RateLimitError, APIConnectionError, APIStatusError

# Configuramos un logger bsico para ver los reintentos en la consola
logger = logging.getLogger(__name__)

T = TypeVar("T")

def with_retry(
    fn: Callable[[], T], 
    max_attempts: int = 3, 
    base_delay: float = 2.0, 
    label: str = "operacin"
) -> T:
    """
    Ejecuta una funcion con reintentos automaticos.
    
    Especialmente diseado para manejar el error 429 (Rate Limit) 
    pausando la ejecucion para permitir que la cuota se regenere.
    """
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            # Intentamos ejecutar la funcion (ej: la llamada a Groq)
            return fn()

        except RateLimitError as e:
            # Si Groq nos dice que vamos muy rapido (Error 429)
            last_exception = e
            if attempt < max_attempts:
                # Aplicamos una pausa de seguridad de al menos 5s
                delay = max(base_delay * (2 ** (attempt - 1)), 5.0)
                logger.warning(
                    f" {label} - Lmite de cuota detectado (Intento {attempt}/{max_attempts}). "
                    f"Reintentando en {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f" {label} - Se agotaron los reintentos por Rate Limit.")

        except (APIConnectionError, APIStatusError) as e:
            # Errores de red o de estado del servidor
            last_exception = e
            if attempt < max_attempts:
                delay = base_delay * (attempt)
                logger.warning(
                    f" {label} - Error de conexin/servidor. Reintentando en {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f" {label} - Fallo critico tras varios intentos.")

        except Exception as e:
            # Si es un error de codigo, no reintentamos para no entrar en bucle
            logger.error(f" Error inesperado en {label}: {e}")
            raise e

    raise last_exception