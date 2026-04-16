from __future__ import annotations


class GeminiClient:
    def __init__(self, model: str) -> None:
        self.model = model

    def classify_contract_type(self, text: str) -> str:
        lowered = text.lower()
        if "non-disclosure" in lowered or "confidential information" in lowered:
            return "NDA"
        if "data processing" in lowered or "processor" in lowered or "subprocessor" in lowered:
            return "DPA"
        if "master services" in lowered or "statement of work" in lowered or "services" in lowered:
            return "MSA"
        return "MSA"

    def propose_redline(self, clause_type: str, original_text: str, fallback_text: str) -> str:
        return f"{fallback_text} [Original replaced for {clause_type.lower()} alignment.]"

    def health(self) -> dict:
        return {"status": "configured", "backend": "gemini", "model": self.model}


GEMINI_CLIENT = GeminiClient(model="gemini-1.5-pro")
