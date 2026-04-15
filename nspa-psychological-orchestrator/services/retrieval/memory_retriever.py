from __future__ import annotations

from domain.narrative.models import NarrativeEpisode


def retrieve_relevant_episodes(episodes: list[NarrativeEpisode], text: str, limit: int = 3) -> list[NarrativeEpisode]:
    lowered = text.lower()
    ranked = []
    for episode in episodes:
        score = 0
        for token in lowered.split():
            if len(token) > 3 and token in f"{episode.user_message} {episode.summary}".lower():
                score += 1
        ranked.append((score, episode))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:limit] if item[0] > 0] or episodes[-limit:]
