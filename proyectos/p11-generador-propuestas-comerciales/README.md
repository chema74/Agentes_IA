# P23 - Agente de ventas y estrategia de negocio

Base publica actual del agente final orientado a ventas y estrategia.

Esta version publica cubre hoy la **generacion de propuestas comerciales entregables** a partir de informacion comercial estructurada. No representa todavia la consolidacion tecnica completa de todas las capacidades derivadas de `P04 + P11 + P16 + P23`.

## Que hace hoy realmente

La aplicacion:
- recoge datos de la empresa, del cliente y de la propuesta,
- genera un borrador comercial estructurado con Groq,
- muestra una preview editable en pantalla,
- exporta el resultado a un archivo Word (`.docx`) listo para revision final.

## Por que sirve como base publica del agente final

Aunque el agente final de ventas y estrategia de negocio integrara progresivamente mas capacidades, esta base publica ya entrega un resultado visible, util y facil de demostrar:

- transformar contexto comercial en una propuesta entregable,
- acelerar preventa y cierre,
- estandarizar la calidad del primer borrador comercial.

## Lo que no afirma esta version

- No integra todavia toda la logica potencial de `P04`, `P11` y `P16`.
- No sustituye la revision comercial final antes de enviar una propuesta.
- No incluye historial, autenticacion ni persistencia de propuestas.

## Stack real

- `streamlit==1.35.0`
- `groq==0.9.0`
- `python-docx==1.1.2`
- `python-dotenv==1.0.1`
- `httpx==0.27.0`

## Requisitos

- Python 3.10+
- `pip`
- `GROQ_API_KEY`

## Instalacion

```bash
cd proyectos/p23-generador-propuestas-comerciales
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Despues, completa `.env` con:

```env
GROQ_API_KEY=tu_api_key_de_groq
```

## Ejecucion

```bash
streamlit run app.py
```

## Flujo real

1. Introduces los datos de tu empresa y del cliente.
2. Defines necesidad, solucion, precio, plazo y tono.
3. Groq devuelve una propuesta estructurada en JSON.
4. La app valida la estructura minima antes de mostrarla.
5. Puedes descargar la propuesta en Word para revisarla y enviarla.

## Estructura esperada de salida

La propuesta generada debe incluir estas secciones:

- `resumen_ejecutivo`
- `problema`
- `solucion`
- `beneficios`
- `metodologia`
- `por_que_nosotros`
- `inversion`
- `siguiente_paso`

## Limites actuales

- Si el modelo no devuelve un JSON valido y completo, la app muestra un error controlado.
- La calidad de la propuesta depende de la calidad del input comercial.
- El documento generado es un borrador profesional, no una version final cerrada sin revision humana.

## Posicionamiento publico recomendado

Puedes comunicarlo asi, sin exagerar capacidades:

> Esta version publica cubre la generacion de propuestas comerciales y actua como base actual del agente final de ventas y estrategia de negocio. Otras capacidades derivadas de proyectos fuente se consolidaran progresivamente sobre esta base.
