from __future__ import annotations

import time
from typing import Callable, TypeVar

from config.settings import MIN_RATE_LIMIT_DELAY
from domain.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    RetryExhaustedError,
)


T = TypeVar("T")


def with_retry(
    fn: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 2.0,
    label: str = "operation",
) -> T:
    del label  # Maintained for compatibility with existing call sites.
    attempt = 0
    last_error: Exception | None = None

    while attempt < max_attempts:
        attempt += 1
        try:
            return fn()
        except ProviderAuthenticationError:
            raise
        except ProviderRateLimitError as exc:
            last_error = exc
            if attempt >= max_attempts:
                break
            delay = max(base_delay * (2 ** (attempt - 1)), float(MIN_RATE_LIMIT_DELAY))
            time.sleep(delay)
        except ProviderTimeoutError as exc:
            last_error = exc
            if attempt >= max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    if last_error is None:
        raise RetryExhaustedError("Retry exhausted.", attempts=attempt)
    raise RetryExhaustedError("Retry exhausted.", attempts=attempt, original=last_error) from last_error
