# Modelo de controles

Un control representa un requisito operativo o de compliance que debe verificarse mediante evidencia trazable.

## Campos base

- `id`
- `scope_id`
- `code`
- `name`
- `description`
- `category`
- `criticality`
- `expected_criterion`
- `status`
- `owner_user_id`
- `version`

## Estados

- `draft`
- `active`
- `deprecated`

## Reglas

- un control sin owner genera un gap operativo
- un control critico no puede considerarse cubierto con mappings de baja confianza
- la cobertura se calcula a partir de mappings y suficiencia de evidencias, no por mera existencia del control
