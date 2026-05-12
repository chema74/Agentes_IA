# Operacion

## Variables criticas

- `SERVICE_API_KEY`
- `NEON_DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SAMBANOVA_API_KEY`

## Persistencia

- `001_init_schema.sql` inicializa el storage operativo del agente.
- `002_supabase_reference_schema.sql` documenta las tablas esperadas para politicas y estado simbolico remotos.

## Despliegue

```bash
docker build -t agente-cumplimiento-politicas .
docker run -p 8040:8040 --env-file .env agente-cumplimiento-politicas
```

## Salud operativa

`GET /api/health` devuelve checks de:

- base de datos operativa
- backend de politicas
- backend de estado simbolico
- configuracion del cliente SambaNova
