# API

## Endpoints

- `GET /api/health`
- `POST /api/change-cases/evaluate`
- `POST /api/change-cases/intervene`
- `GET /api/change-cases/{case_id}`
- `GET /api/audit/{reference}`

## Health

`GET /api/health`

Devuelve estado del servicio, modo activo y checks de storage y LLM.

Ejemplo:

```json
{
  "status": "ok",
  "service": "orquestador-coaching-cambio",
  "mode": "case=sql-backed;cache=memory;vector=noop-vector",
  "require_api_key": true,
  "checks": {
    "storage": {
      "case_store": { "status": "ok", "backend": "sqlite" },
      "cache_store": { "status": "ok", "backend": "memory" },
      "vector_store": { "status": "ok", "backend": "noop-vector" }
    },
    "groq": { "status": "configured", "backend": "groq", "model": "llama3-8b-8192" },
    "gemini": { "status": "configured", "backend": "gemini", "model": "gemini-1.5-pro" }
  }
}
```

## Payload de entrada

`POST /api/change-cases/evaluate`

`POST /api/change-cases/intervene`

Campos:

- `process_notes`: texto libre principal del caso
- `context_type`: `organizational` o `individual`
- `change_goal`: objetivo explicito del cambio
- `change_phase`: fase del proceso, por ejemplo `assessment`, `adoption`, `stabilization`
- `requested_mode`: intencion del caller, por ejemplo `evaluate` o `intervene`
- `case_id`: opcional
- `signals[]`: senales ya estructuradas
- `stakeholders[]`: stakeholders ya estructurados
- `sessions[]`: notas de sesiones
- `tasks[]`: tareas asociadas al cambio
- `survey_inputs[]`: respuestas o sintomas recogidos por encuesta
- `source_systems[]`: referencia a sistemas de origen

### Ejemplo de entrada

```json
{
  "process_notes": "Existe ambiguedad sobre prioridades. El equipo muestra fatiga y retrasos.",
  "context_type": "organizational",
  "change_goal": "Recuperar claridad y continuidad en la adopcion del cambio",
  "change_phase": "assessment",
  "requested_mode": "evaluate",
  "sessions": [
    {
      "summary": "En la reunion semanal aparecieron dudas repetidas sobre la secuencia del cambio.",
      "source": "weekly_checkin",
      "sentiment": "tense"
    }
  ],
  "tasks": [
    {
      "title": "Definir responsables de la nueva operativa",
      "status": "blocked",
      "owner": "lider_de_area",
      "due_window": "esta semana"
    }
  ],
  "survey_inputs": [
    {
      "prompt": "Como describirias el ritmo del cambio",
      "response": "Demasiado alto y poco claro",
      "score": 2
    }
  ]
}
```

## Contrato de salida

Toda evaluacion e intervencion devuelve:

- `estado_del_proceso_de_cambio`
- `resumen_de_senales_detectadas`
- `mapa_de_stakeholders_o_contexto_personal`
- `perfil_de_resistencia`
- `bloqueos_de_adopcion_detectados`
- `nivel_de_friccion`
- `plan_de_intervencion`
- `hitos_de_transformacion`
- `alerta_de_fatiga_de_cambio`
- `revision_humana_requerida`
- `estado_de_la_puerta_de_supervision_humana`
- `recomendacion_final`
- `referencia_de_auditoria`
- `case_id`

### Ejemplo de salida

```json
{
  "estado_del_proceso_de_cambio": "relevant_friction",
  "resumen_de_senales_detectadas": [
    {
      "signal_id": "signal-123",
      "category": "ambiguity",
      "summary": "Existe ambiguedad sobre prioridades",
      "intensity": "medium",
      "source": "direct_input",
      "domain": "change_process",
      "evidence_excerpt": "Existe ambiguedad sobre prioridades",
      "interpretation_status": "observed",
      "confidence": 0.72,
      "observed_at": "2026-04-16T00:00:00Z"
    }
  ],
  "mapa_de_stakeholders_o_contexto_personal": [
    {
      "actor": "lider",
      "role": "sponsor",
      "influence": "high",
      "alignment": "partial",
      "resistance_level": "medium",
      "readiness_level": "emergent",
      "support_needed": "decision clarity",
      "notes": "Necesita clarificar prioridades y secuencia del cambio."
    }
  ],
  "perfil_de_resistencia": {
    "resistance_type": "overload",
    "intensity": "medium",
    "rationale": "Resistance profile derived from repeated friction signals and execution patterns.",
    "legitimacy": "legitimate",
    "manifestations": ["sobrecarga y fatiga de cambio"],
    "inferred_from_signal_ids": ["signal-123"],
    "confidence": 0.84
  },
  "bloqueos_de_adopcion_detectados": [
    {
      "blocker": "clarity_gap",
      "blocker_type": "clarity",
      "impact": "moderate",
      "recommended_response": "Clarify sequence, responsibilities, and near-term decision rights.",
      "owner": "responsable_del_cambio",
      "evidence": "Repeated ambiguity signals were detected.",
      "escalation_hint": "Escalar si la ambiguedad persiste tras una conversacion de aclaracion."
    }
  ],
  "nivel_de_friccion": {
    "level": "medium",
    "confidence": 0.85,
    "process_status": "en_friccion",
    "friction_sources": ["ambiguity", "fatigue"],
    "adoption_maturity": "emergent",
    "discourse_execution_gap": "low",
    "difficult_conversations_pending": false
  },
  "plan_de_intervencion": {
    "focus": "proportional_change_intervention",
    "intervention_mode": "proportional",
    "sequencing_rationale": "Primero claridad y bloqueo principal, despues acompanamiento y consolidacion.",
    "escalation_conditions": [
      "Persistencia de fatiga alta",
      "Incoherencia fuerte entre discurso y ejecucion",
      "Conversacion dificil no realizada"
    ],
    "steps": [
      {
        "step": "Explicitar que esta cambiando, por que, con que impacto y en que secuencia.",
        "owner": "responsable_del_cambio",
        "timing": "48h",
        "intervention_type": "clarification",
        "objective": "Reducir ambiguedad y alinear expectativas inmediatas.",
        "success_metric": "Existe una narrativa comun del cambio y responsables claros para la siguiente semana."
      }
    ]
  },
  "hitos_de_transformacion": [
    {
      "milestone": "claridad_del_cambio",
      "status": "pendiente",
      "evidence": "El proceso requiere una narrativa compartida del cambio.",
      "owner": "responsable_del_cambio"
    }
  ],
  "alerta_de_fatiga_de_cambio": {
    "level": "medium",
    "evidence": "Detected fatigue and overload signals.",
    "contributors": ["El equipo muestra fatiga y retrasos"],
    "confidence": 0.8
  },
  "revision_humana_requerida": false,
  "estado_de_la_puerta_de_supervision_humana": {
    "status": "monitoring",
    "owner": "lider_del_proceso",
    "rationale": "Keep human oversight with light monitoring.",
    "next_review_action": "Seguimiento ligero con foco en senales nuevas.",
    "automation_allowed": true
  },
  "recomendacion_final": {
    "summary": "Intervencion proporcional y seguimiento.",
    "level": 2,
    "rationale": "La proporcionalidad final depende del nivel de friccion, la resistencia y el breaker.",
    "automation_mode": "monitored",
    "next_best_owner": "lider_del_proceso"
  },
  "referencia_de_auditoria": "audit-abc",
  "case_id": "case-abc"
}
```

## Semantica de niveles

- `observation`: adaptacion esperable, seguimiento ligero
- `relevant_friction`: friccion relevante, intervencion puntual
- `change_compromised`: proceso comprometido, revision humana
- `circuit_breaker`: detener automatizacion fuerte y transferir control

## Auditoria

`GET /api/audit/{reference}`

Devuelve la traza asociada a la referencia de auditoria del caso.
