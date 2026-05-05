from __future__ import annotations

import json
import os

try:
    from groq import Groq
except ImportError:  # pragma: no cover - optional dependency in CI
    Groq = None


class GroqClient:
    def __init__(self, model: str) -> None:
        self.model = model
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key and Groq else None

    def classify_signal(self, text: str) -> tuple[str, str]:
        """
        Clasifica una senal organizativa devolviendo:
        - category
        - intensity

        Intenta usar Groq real.
        Si falla o no hay API key, cae a un fallback heuristico local.
        """
        if not self.client:
            return self._fallback_classify(text)

        prompt = f"""
Analiza este texto sobre un proceso de cambio organizativo.

Debes elegir la senal PRINCIPAL mas relevante.

Prioridades de clasificacion:
1. interpersonal_conflict -> si hay tension, conflicto, choque entre responsables o friccion relacional
2. fatigue -> si hay cansancio, saturacion, sobrecarga o agotamiento del equipo
3. execution_block -> si hay retrasos, bloqueos, dependencias o imposibilidad de avanzar
4. ambiguity -> si hay falta de claridad o confusion
5. passive_resistance -> si hay resistencia pasiva o no colaboracion indirecta
6. adaptation -> si no aplica ninguna anterior

Intensidad:
- high -> senal fuerte y explicita
- medium -> senal clara pero no extrema
- low -> senal debil o secundaria

Devuelve SOLO JSON valido con este formato exacto:
{{"category":"...", "intensity":"..."}}

Texto:
{text}
""".strip()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un clasificador estricto de senales de cambio organizativo. Responde solo con JSON valido.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            content = response.choices[0].message.content.strip()
            data = json.loads(content)

            category = str(data.get("category", "adaptation")).strip()
            intensity = str(data.get("intensity", "low")).strip()

            valid_categories = {
                "fatigue",
                "ambiguity",
                "execution_block",
                "interpersonal_conflict",
                "passive_resistance",
                "adaptation",
            }
            valid_intensities = {"low", "medium", "high"}

            if category not in valid_categories:
                category = "adaptation"
            if intensity not in valid_intensities:
                intensity = "low"

            return category, intensity

        except Exception:
            return self._fallback_classify(text)

    def _fallback_classify(self, text: str) -> tuple[str, str]:
        """
        Clasificacin local basica por palabras clave.
        Se usa cuando Groq no est disponible o falla la llamada.
        """
        lowered = text.lower()

        if any(word in lowered for word in ["conflicto", "tension", "tension", "choque", "friccion relacional", "friccion relacional"]):
            return "interpersonal_conflict", "high"

        if any(word in lowered for word in ["agotado", "agotada", "cansado", "cansada", "fatiga", "saturado", "saturada", "sobrecarga"]):
            return "fatigue", "high"

        if any(word in lowered for word in ["retraso", "retrasos", "bloqueo", "bloqueos", "dependencia", "dependencias", "no avanza", "no avanzar"]):
            return "execution_block", "high"

        if any(word in lowered for word in ["ambiguedad", "ambiguedad", "no entiendo", "confusion", "confusion", "falta de claridad"]):
            return "ambiguity", "medium"

        if any(word in lowered for word in ["resistencia pasiva", "no colabora", "no colaboran", "pasividad"]):
            return "passive_resistance", "medium"

        return "adaptation", "low"

    def health(self) -> dict:
        return {
            "status": "configured" if self.client else "fallback_only",
            "backend": "groq",
            "model": self.model,
        }


GROQ_CLIENT = GroqClient(
    model=os.getenv("GROQ_MODEL", "llama3-8b-8192")
)
