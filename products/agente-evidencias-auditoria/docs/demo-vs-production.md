# Demo vs produccion

## Modo demo

- usuarios mock
- datos anonimos
- storage local con misma interfaz que el adaptador de Supabase
- workflow completo demostrable sin red
- pensado para discovery, demos y validacion interna

## Modo produccion

- Supabase Auth real
- Postgres real
- Storage real en buckets segregados
- endurecimiento de secretos y sesiones
- politicas de acceso y trazabilidad mas estrictas
- integraciones con fuentes reales de evidencias

## Lo que no cambia

- el dominio
- la logica de mapping y evaluacion
- la estructura de evidencias, hallazgos y remediaciones
- la necesidad de revision humana en decisiones sensibles
