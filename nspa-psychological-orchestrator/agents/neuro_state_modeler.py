from __future__ import annotations

from domain.affect.models import NeuroState


NEGATIVE_WEIGHTS = {
    "sadness": {"serotonin": -0.15, "valence": -0.2, "cortisol": 0.1},
    "anxiety": {"cortisol": 0.2, "arousal": 0.2, "emotional_stability": -0.15},
    "fear": {"cortisol": 0.18, "arousal": 0.18, "valence": -0.12},
    "guilt": {"valence": -0.15, "dopamine": -0.1},
    "loneliness": {"oxytocin": -0.18, "valence": -0.1},
    "exhaustion": {"dopamine": -0.16, "emotional_stability": -0.12},
    "overwhelm": {"cortisol": 0.15, "arousal": 0.15, "emotional_stability": -0.12},
}


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))


def update_neuro_state(user_id: str, prior: NeuroState | None, affective_labels: list[str]) -> NeuroState:
    state = prior or NeuroState(user_id=user_id)
    payload = state.model_dump()
    for label in affective_labels:
        for key, delta in NEGATIVE_WEIGHTS.get(label, {}).items():
            payload[key] = _bounded(payload[key] + delta)
    return NeuroState(**payload)
