from __future__ import annotations

import re


class LiteLLMGateway:
    def __init__(self, model: str, fallback_model: str | None = None) -> None:
        self.model = model
        self.fallback_model = fallback_model

    def summarize(self, title: str, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return f"{title}: {' '.join(sentences[:4]).strip()}"

    def propose_mapping_rationale(self, control_text: str, evidence_text: str) -> str:
        return f"Relacion sugerida por coincidencia de terminos entre control y evidencia. Control: {control_text[:120]} Evidence: {evidence_text[:120]}"

    def propose_finding_recommendation(self, gap_type: str) -> str:
        return f"Revisar el gap {gap_type} y validar si requiere evidencia adicional o remediacion formal."
