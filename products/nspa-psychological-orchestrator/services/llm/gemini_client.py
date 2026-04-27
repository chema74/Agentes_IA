from __future__ import annotations

from core.config.settings import settings


class GeminiClient:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.gemini_model

    def summarize(self, text: str) -> str:
        shortened = text.strip().replace("\n", " ")
        return shortened[:220] if shortened else "Sin contenido suficiente para resumir."

    def generate_supportive_reframe(self, text: str) -> str:
        return f"Reencuadre prudente basado en el mensaje: {text[:180]}"
