# P01 - Inteligencia comercial internacional

La pieza de portfolio mas avanzada del bloque. Compara mercados internacionales con apoyo de busqueda web en tiempo real y analisis estructurado por dimensiones para apoyar decisiones de internacionalizacion.

## Que problema resuelve

Evaluar la viabilidad comercial en varios paises requiere contrastar indicadores de mercado, riesgo regulatorio, competencia local y capacidad de entrada. Este agente recupera senales actualizadas de cada mercado, las analiza por dimensiones y genera un ranking orientativo con resumen ejecutivo, facilitando la primera criba antes de invertir en estudios de mercado detallados.

## Que hace

- Busca senales relevantes de mercado para cada pais con web search (Tavily).
- Genera analisis estructurado por dimensiones: oportunidad, riesgo, competencia, regulacion, logistica.
- Compara varios paises en paralelo y calcula un ranking orientativo.
- Exporta resultados en multiples formatos (PDF, Excel, JSON).
- Guarda un historial basico de analisis anteriores para comparacion.

## Stack

- Groq (LLama 3.3 70B)
- Tavily (busqueda web en tiempo real)
- Streamlit
- Pydantic (validacion de datos estructurados)
- pandas (comparativas y exportacion)

## Flujo principal

1. Selecciona uno o varios paises a comparar.
2. Elige sector y tipo de empresa exportadora.
3. El agente recupera contexto con busqueda web y lo analiza dimension a dimension.
4. Revisa el resumen ejecutivo, las senales por dimension y el ranking comparativo.
5. Exporta o consulta el historial de analisis previos.

## Interpretacion del score

El indicador `score_total` es un indice orientativo de riesgo y oportunidad calculado a partir de las senales recuperadas:

- **Menor score = mejor posicion relativa** para ese mercado.
- No es un rating certificado ni sustituye due diligence completa.
- No reemplaza asesoria juridica, fiscal o logistica especializada.

## Instalacion

```bash
cd portfolio/p01-inteligencia-comercial-internacional
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edita .env con GROQ_API_KEY y TAVILY_API_KEY
streamlit run app.py
```

## Estado

Pieza de portfolio cerrada tecnicamente. Es la referencia principal del bloque de inteligencia comercial internacional y la demo mas completa del portfolio. Para un agente de trade intelligence con cobertura geopolitica y evaluacion de rutas consulta el producto agente-inteligencia-geopolitica del repositorio.
