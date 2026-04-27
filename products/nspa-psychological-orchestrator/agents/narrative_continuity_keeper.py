from __future__ import annotations

from domain.narrative.models import NarrativeEpisode


def continuity_notes_from_history(episodes: list[NarrativeEpisode]) -> str:
    if not episodes:
        return "Sin episodios previos; iniciar continuidad desde esta interaccion."
    last = episodes[-1]
    return f"Ultimo episodio recordado: {last.summary}. Continuidad previa: {last.continuity_notes}"
