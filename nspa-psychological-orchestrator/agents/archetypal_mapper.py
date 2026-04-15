from __future__ import annotations

from domain.archetypes.models import ArchetypeProfile


ARCHETYPES = {
    "control": ArchetypeProfile(dominant_archetype="guardian", narrative_pattern="busqueda de seguridad y orden", symbolic_notes="Necesidad de sostener estructura cuando aparece incertidumbre."),
    "culpa": ArchetypeProfile(dominant_archetype="judge", narrative_pattern="autoexigencia y deuda moral", symbolic_notes="Conviene reducir fusion con el juicio interno."),
    "soledad": ArchetypeProfile(dominant_archetype="exile", narrative_pattern="aislamiento y desconexion", symbolic_notes="La intervencion debe favorecer vinculo y validacion."),
}


def map_archetype(text: str) -> ArchetypeProfile:
    lowered = text.lower()
    if "control" in lowered or "orden" in lowered:
        return ARCHETYPES["control"]
    if "culpa" in lowered or "fracaso" in lowered:
        return ARCHETYPES["culpa"]
    if "solo" in lowered or "nadie" in lowered:
        return ARCHETYPES["soledad"]
    return ArchetypeProfile(dominant_archetype="witness", narrative_pattern="observacion de malestar sin patron dominante estable", symbolic_notes="No usar marco simbolico fuerte cuando la evidencia narrativa es debil.")
