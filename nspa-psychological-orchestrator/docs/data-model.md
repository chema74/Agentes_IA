# Modelo de datos

## Entidades principales

- `NEURO_STATE`
- `ARCHETYPE_PROFILE`
- `NARRATIVE_EPISODE`
- `CBT_INTERVENTION`
- `RISK_EVENT`

## Contrato de salida

Toda respuesta del orquestador devuelve:

- `affective_state`
- `inferred_risk_level`
- `continuity_notes`
- `validated_signals`
- `intervention_style`
- `recommended_next_step`
- `escalation_status`
- `safety_notes`
- `narrative_memory_reference`
