# P01 - Inteligencia comercial internacional

Base publica del agente de portfolio orientado a comparar paises y mercados para apoyar decisiones comerciales internacionales.

## Que hace

- Busca senales relevantes de mercado con apoyo de web search.
- Genera analisis estructurados por dimensiones.
- Compara varios paises.
- Calcula un ranking orientativo de mercados.
- Guarda un historial basico de resultados.

## Stack

- Groq
- Tavily
- Streamlit
- Pydantic
- pandas

## Flujo principal

1. Selecciona uno o varios paises a comparar.
2. Elige sector y tipo de empresa.
3. Recupera contexto con busqueda web y analisis asistido por modelo.
4. Revisa resumen ejecutivo, senales por dimension y comparativa orientativa.
5. Consulta el historial cuando existan datos previos.

## Interpretacion del score

El indicador principal es `score_total`, un indice orientativo de riesgo y oportunidad:

- menor score = mejor posicion relativa,
- no es un rating certificado,
- no sustituye una due diligence completa ni una asesoria juridica.

## Instalacion

```bash
cd portfolio/p01-inteligencia-comercial-internacional
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## Estado

Es la base publica mas avanzada del portfolio y la referencia principal del bloque de inteligencia comercial internacional.
