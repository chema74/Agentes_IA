# ROI

Las hipótesis editables viven en `assumptions.yaml`.

La calculadora es deliberadamente transparente:

- horas de revisión por contrato
- contratos al mes
- coste por hora
- ahorro por extracción
- ahorro por seguimiento
- estimación de reducción de omisiones
- ahorro mensual y anual
- payback estimado

La calculadora expone un desglose para que las hipótesis se puedan auditar:

- coste base de revisión manual
- ahorro por extracción
- ahorro por seguimiento
- ahorro por omisiones
- ahorro mensual total
- ahorro anual
- payback en meses

Ejecuta `python -m roi.calculator` desde la raíz del proyecto para imprimir el desglose actual en JSON.
