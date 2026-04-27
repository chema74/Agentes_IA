from types import SimpleNamespace

import httpx
import pytest

from domain import analysis
from domain.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
)


class FakeChoice:
    def __init__(self, content: str):
        self.message = SimpleNamespace(content=content)


class FakeResponse:
    def __init__(self, content: str):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, side_effects):
        self.side_effects = side_effects
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)

        effect = self.side_effects.pop(0)
        if isinstance(effect, Exception):
            raise effect
        return effect


class FakeChat:
    def __init__(self, completions):
        self.completions = completions


class FakeGroq:
    def __init__(self, side_effects):
        self.chat = FakeChat(FakeCompletions(side_effects))


def build_contexto():
    return {
        "politico": "Contexto político de prueba",
        "economico": "Contexto económico de prueba",
        "regulatorio": "Contexto regulatorio de prueba",
        "oportunidades": "Oportunidades de prueba",
    }


def build_httpx_response(status_code: int):
    """
    Construye una respuesta HTTP mínima válida para instanciar
    excepciones reales del SDK de Groq durante los tests.
    """
    request = httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/chat/completions",
    )
    return httpx.Response(status_code=status_code, request=request)


def build_rate_limit_error(message: str):
    return analysis.RateLimitError(
        message,
        response=build_httpx_response(429),
        body={"error": {"message": message}},
    )


def build_authentication_error(message: str):
    return analysis.AuthenticationError(
        message,
        response=build_httpx_response(401),
        body={"error": {"message": message}},
    )


def test_analizar_pais_ok_with_primary_model(monkeypatch):
    monkeypatch.setattr(analysis, "MODEL_NAME", "modelo-principal")
    monkeypatch.setattr(analysis, "FALLBACK_MODEL_NAME", "modelo-fallback")
    monkeypatch.setattr(analysis, "ENABLE_LLM_FALLBACK", True)

    groq = FakeGroq(
        side_effects=[
            FakeResponse(
                '{"pais":"México","resumen_ejecutivo":"OK","alertas":["a","b","c"],"oportunidades":["x","y","z"]}'
            )
        ]
    )

    result = analysis.analizar_pais(
        groq=groq,
        pais="México",
        sector="Tecnología",
        tipo="PYME exportadora",
        contexto=build_contexto(),
    )

    assert '"pais":"México"' in result
    assert len(groq.chat.completions.calls) == 1
    assert groq.chat.completions.calls[0]["model"] == "modelo-principal"


def test_analizar_pais_uses_fallback_after_rate_limit(monkeypatch):
    monkeypatch.setattr(analysis, "MODEL_NAME", "modelo-principal")
    monkeypatch.setattr(analysis, "FALLBACK_MODEL_NAME", "modelo-fallback")
    monkeypatch.setattr(analysis, "ENABLE_LLM_FALLBACK", True)

    groq = FakeGroq(
        side_effects=[
            build_rate_limit_error("rate limit on primary"),
            FakeResponse(
                '{"pais":"México","resumen_ejecutivo":"OK Fallback","alertas":["a","b","c"],"oportunidades":["x","y","z"]}'
            ),
        ]
    )

    result = analysis.analizar_pais(
        groq=groq,
        pais="México",
        sector="Tecnología",
        tipo="PYME exportadora",
        contexto=build_contexto(),
    )

    assert "OK Fallback" in result
    assert len(groq.chat.completions.calls) == 2
    assert groq.chat.completions.calls[0]["model"] == "modelo-principal"
    assert groq.chat.completions.calls[1]["model"] == "modelo-fallback"


def test_analizar_pais_authentication_error(monkeypatch):
    monkeypatch.setattr(analysis, "MODEL_NAME", "modelo-principal")
    monkeypatch.setattr(analysis, "FALLBACK_MODEL_NAME", "modelo-fallback")
    monkeypatch.setattr(analysis, "ENABLE_LLM_FALLBACK", True)

    groq = FakeGroq(
        side_effects=[
            build_authentication_error("invalid api key"),
        ]
    )

    with pytest.raises(ProviderAuthenticationError):
        analysis.analizar_pais(
            groq=groq,
            pais="México",
            sector="Tecnología",
            tipo="PYME exportadora",
            contexto=build_contexto(),
        )


def test_analizar_pais_rate_limit_error_when_all_models_fail(monkeypatch):
    monkeypatch.setattr(analysis, "MODEL_NAME", "modelo-principal")
    monkeypatch.setattr(analysis, "FALLBACK_MODEL_NAME", "modelo-fallback")
    monkeypatch.setattr(analysis, "ENABLE_LLM_FALLBACK", True)

    groq = FakeGroq(
        side_effects=[
            build_rate_limit_error("primary rate limit"),
            build_rate_limit_error("fallback rate limit"),
        ]
    )

    with pytest.raises(ProviderRateLimitError):
        analysis.analizar_pais(
            groq=groq,
            pais="México",
            sector="Tecnología",
            tipo="PYME exportadora",
            contexto=build_contexto(),
        )


def test_comparar_paises_ok(monkeypatch):
    monkeypatch.setattr(analysis, "MODEL_NAME", "modelo-principal")
    monkeypatch.setattr(analysis, "FALLBACK_MODEL_NAME", "modelo-fallback")
    monkeypatch.setattr(analysis, "ENABLE_LLM_FALLBACK", True)

    groq = FakeGroq(
        side_effects=[
            FakeResponse("México parece mejor candidato con cautelas regulatorias.")
        ]
    )

    result = analysis.comparar_paises(
        groq=groq,
        pais_a="México",
        pais_b="Colombia",
        resultado_a={"resumen_ejecutivo": "A"},
        resultado_b={"resumen_ejecutivo": "B"},
        sector="Tecnología",
        tipo="PYME exportadora",
    )

    assert "México" in result
    assert len(groq.chat.completions.calls) == 1
    assert groq.chat.completions.calls[0]["max_tokens"] == 600