from __future__ import annotations


class GroqClient:
    def __init__(self, model: str) -> None:
        self.model = model

    def classify_signal(self, text: str) -> tuple[str, str]:
        lowered = text.lower()
        if "cansancio" in lowered or "fatiga" in lowered or "agotado" in lowered:
            return "fatigue", "high"
        if "no entiendo" in lowered or "ambigu" in lowered:
            return "ambiguity", "medium"
        if "retras" in lowered or "bloque" in lowered:
            return "execution_block", "high"
        if "conflicto" in lowered or "tension" in lowered:
            return "interpersonal_conflict", "high"
        return "adaptation", "low"

    def health(self) -> dict:
        return {"status": "configured", "backend": "groq", "model": self.model}


GROQ_CLIENT = GroqClient(model="llama3-8b-8192")
