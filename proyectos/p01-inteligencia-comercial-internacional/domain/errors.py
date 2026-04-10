from __future__ import annotations


class AppBaseError(Exception):
    """Error base de la aplicación."""
    pass


class ExternalServiceError(AppBaseError):
    """Error genérico al invocar un servicio externo."""

    def __init__(self, message: str = "", service: str = "", original: Exception | None = None):
        super().__init__(message)
        self.service = service
        self.original = original


class ProviderAuthenticationError(ExternalServiceError):
    """Error de autenticación contra el proveedor LLM."""
    pass


class ProviderRateLimitError(ExternalServiceError):
    """Error por límite de cuota o rate limit del proveedor LLM."""
    pass


class ProviderTimeoutError(ExternalServiceError):
    """Error por timeout al invocar el proveedor LLM."""
    pass


class ProviderResponseError(ExternalServiceError):
    """Error por respuesta inválida o inesperada del proveedor."""
    pass


class RetryExhaustedError(ExternalServiceError):
    """Se agotaron todos los reintentos sin éxito."""

    def __init__(self, message: str = "", attempts: int = 0, original: Exception | None = None):
        super().__init__(message, original=original)
        self.attempts = attempts