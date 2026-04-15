from __future__ import annotations

from core.config.settings import settings


class GeminiEvaluatorClient:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.gemini_model

    def summarize_learning_process(self, text: str) -> str:
        return text.strip().replace("\n", " ")[:220] or "Sin proceso suficiente para resumir."
