from __future__ import annotations

import re


class LiteLLMGateway:
    def __init__(self, model: str, fallback_model: str | None = None) -> None:
        self.model = model
        self.fallback_model = fallback_model

    def summarize(self, title: str, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return f"{title}: {' '.join(sentences[:5]).strip()}"

    def compare_to_checklist(self, text: str, checklist_items: list[str]) -> list[str]:
        lower = text.lower()
        return [item for item in checklist_items if item.lower() not in lower]

