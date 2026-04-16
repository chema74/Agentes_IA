from __future__ import annotations


class GeminiClient:
    def __init__(self, model: str) -> None:
        self.model = model

    def deepen_memorandum(self, summary: str) -> str:
        return f"Memorando ampliado: {summary}"

    def health(self) -> dict:
        return {"status": "configured", "backend": "gemini", "model": self.model}


GEMINI_CLIENT = GeminiClient(model="gemini-1.5-pro")
