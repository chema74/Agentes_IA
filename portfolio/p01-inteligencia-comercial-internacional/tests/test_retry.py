"""
Tests para infrastructure/retry.py — Fase 18B
Verifica la lógica de reintentos y la pausa de seguridad (Rate Limit).
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from infrastructure.retry import with_retry
from domain.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    RetryExhaustedError,
)
from config.settings import MIN_RATE_LIMIT_DELAY  # FASE 18B


def test_with_retry_succeeds_on_first_attempt():
    fn = MagicMock(return_value="ok")
    # Usamos base_delay=0 para que el test sea instantáneo
    result = with_retry(fn, max_attempts=3, base_delay=0, label="test")
    assert result == "ok"
    assert fn.call_count == 1


@patch("time.sleep")
def test_with_retry_succeeds_on_second_attempt(mock_sleep):
    fn = MagicMock(side_effect=[ProviderTimeoutError("timeout"), "ok"])
    result = with_retry(fn, max_attempts=3, base_delay=1.0, label="test")
    assert result == "ok"
    assert fn.call_count == 2
    # Verifica que se llamó a sleep con el delay base
    mock_sleep.assert_called_once_with(1.0)


@patch("time.sleep")
def test_with_retry_handles_rate_limit_with_min_delay(mock_sleep):
    """
    FASE 18B: Verifica que ante un Rate Limit se aplique el MIN_RATE_LIMIT_DELAY
    si el backoff calculado es menor.
    """
    fn = MagicMock(side_effect=[ProviderRateLimitError("limit"), "ok"])
    # Aunque base_delay sea 0.1, debe aplicar el mínimo de settings (ej: 5.0s)
    result = with_retry(fn, max_attempts=3, base_delay=0.1, label="test")
    
    assert result == "ok"
    assert fn.call_count == 2
    
    # El primer argumento de la primera llamada a sleep debe ser >= MIN_RATE_LIMIT_DELAY
    llamada_sleep = mock_sleep.call_args_list[0][0][0]
    assert llamada_sleep >= MIN_RATE_LIMIT_DELAY


def test_with_retry_exhausts_all_attempts():
    fn = MagicMock(side_effect=ProviderTimeoutError("timeout"))
    with pytest.raises(RetryExhaustedError) as exc_info:
        with_retry(fn, max_attempts=3, base_delay=0, label="test")
    assert exc_info.value.attempts == 3
    assert fn.call_count == 3


def test_with_retry_no_retry_on_auth_error():
    fn = MagicMock(side_effect=ProviderAuthenticationError("auth"))
    with pytest.raises(ProviderAuthenticationError):
        with_retry(fn, max_attempts=3, base_delay=0, label="test")
    assert fn.call_count == 1


def test_with_retry_no_retry_on_unexpected_error():
    fn = MagicMock(side_effect=ValueError("unexpected"))
    with pytest.raises(ValueError):
        with_retry(fn, max_attempts=3, base_delay=0, label="test")
    assert fn.call_count == 1


# --- Tests de estructura de Errores ---

def test_retry_exhausted_error_stores_attempts():
    err = RetryExhaustedError("agotado", attempts=3)
    assert err.attempts == 3


def test_retry_exhausted_error_stores_original():
    original = ProviderRateLimitError("rate")
    err = RetryExhaustedError("agotado", attempts=2, original=original)
    assert err.original is original