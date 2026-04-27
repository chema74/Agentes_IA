from __future__ import annotations


class GroqClient:
    def __init__(self, model: str) -> None:
        self.model = model

    def classify_signal(self, text: str) -> tuple[str, str]:
        lowered = text.lower()
        if "sanction" in lowered or "sancion" in lowered or "export control" in lowered:
            return "sanction", "critical"
        if "port" in lowered or "canal" in lowered or "route" in lowered or "desvio" in lowered:
            return "route", "high"
        if "tariff" in lowered or "arancel" in lowered or "licence" in lowered or "licencia" in lowered:
            return "trade_policy", "high"
        if "election" in lowered or "conflict" in lowered or "tension" in lowered:
            return "country_risk", "medium"
        return "context", "low"

    def health(self) -> dict:
        return {"status": "configured", "backend": "groq", "model": self.model}


GROQ_CLIENT = GroqClient(model="llama3-8b-8192")
