from __future__ import annotations

from domain.stakeholders.models import StakeholderEntry


def _default_stakeholders(context_type: str) -> list[StakeholderEntry]:
    if context_type == "individual":
        return [
            StakeholderEntry(
                actor="persona",
                role="protagonista_del_cambio",
                influence="high",
                alignment="mixed",
                resistance_level="medium",
                readiness_level="emergent",
                support_needed="reflection, sequencing, and realistic pacing",
                notes="Perfil individual sin otros actores explicitados.",
            )
        ]
    return [
        StakeholderEntry(
            actor="lider",
            role="sponsor",
            influence="high",
            alignment="partial",
            resistance_level="medium",
            readiness_level="emergent",
            support_needed="decision clarity",
            notes="Necesita clarificar prioridades y secuencia del cambio.",
        ),
        StakeholderEntry(
            actor="equipo",
            role="adopter_group",
            influence="high",
            alignment="mixed",
            resistance_level="medium",
            readiness_level="fragile",
            support_needed="capacity and communication",
            notes="La capacidad de absorcion del cambio parece tensionada.",
        ),
    ]


def map_stakeholders(context_type: str, provided: list[StakeholderEntry] | None = None) -> list[StakeholderEntry]:
    if provided:
        return provided
    return _default_stakeholders(context_type)
