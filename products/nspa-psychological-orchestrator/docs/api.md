# API

## Endpoints

- `GET /api/health`
- `POST /api/support`

## POST /api/support

Entrada:

```json
{
  "user_id": "user-001",
  "message": "No puedo mas con esto y me siento muy solo"
}
```

Salida:

Incluye el estado afectivo inferido, nivel de riesgo, notas de continuidad, estilo de intervencion, siguiente paso recomendado y estado de escalado.
