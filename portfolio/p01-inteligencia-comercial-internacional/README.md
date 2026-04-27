# P01 - Inteligencia comercial internacional

> Portfolio IA Aplicada - Txema Rios - Sevilla  
> Stack: Groq - Tavily - Streamlit - Pydantic - pandas

## Que hace hoy este proyecto

Esta es la base publica actual del agente final Agente de inteligencia comercial internacional.

Su funcion actual es ayudar a comparar paises y mercados para apoyar decisiones comerciales internacionales mediante:

- busqueda web asistida sobre senales relevantes de mercado,
- analisis estructurado por dimensiones,
- comparacion entre paises,
- ranking orientativo de mercados,
- historial basico de resultados.

No se presenta como un sistema formal de rating pais, una due diligence completa ni una asesoria juridica o regulatoria.

## Flujo principal

1. Seleccionar uno o varios paises a comparar.
2. Elegir sector y tipo de empresa.
3. Recuperar contexto con busqueda web y analisis asistido por modelo.
4. Mostrar resumen ejecutivo, senales por dimension y comparativa orientativa.
5. Revisar ranking o historial cuando existan datos previos.

## Que entrega

- resumen ejecutivo por pais,
- senales por dimension para apoyar la comparacion,
- comparativa entre dos mercados,
- ranking orientativo de varios paises,
- panel historico con resultados guardados por la aplicacion.

## Interpretacion del score orientativo

El indicador principal visible al usuario es un indice orientativo de riesgo (internamente `score_total`):

- mide una estimacion comparativa de senales de riesgo y oportunidad sin presentarse como una escala fija o certificada,
- menor score = mejor posicion relativa para priorizacion comparativa,
- no es un rating certificado ni un veredicto de entrada a mercado.

## Instalacion y ejecucion local

```bash
cd portfolio/p01-inteligencia-comercial-internacional
pyenv local 3.11.9
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app/streamlit_app.py
```

## Ejecucion de tests

```bash
cd portfolio/p01-inteligencia-comercial-internacional
pytest -q
```

## Deploy minimo en Streamlit Cloud

- Entry point: `portfolio/p01-inteligencia-comercial-internacional/app/streamlit_app.py`
- Requirements file: `portfolio/p01-inteligencia-comercial-internacional/requirements.txt`

*Portfolio IA Aplicada - Txema Rios - Sevilla - 2026*
