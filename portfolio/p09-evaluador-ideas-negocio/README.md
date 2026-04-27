# P09 - Evaluador de ideas de negocio

Demo de portfolio para valorar una idea de negocio con apoyo de IA y busqueda web.

## Que hace

Describe tu idea de negocio y recibes un analisis estructurado con:

- puntuacion global de 1 a 10,
- analisis por dimensiones: mercado, diferenciacion, viabilidad, ejecucion y timing,
- DAFO resumido,
- competidores clave,
- modelo de negocio sugerido,
- plan de validacion,
- consejo directo y accionable.

## Stack

- Groq
- Tavily
- Streamlit

## Como ejecutarlo

```bash
cd portfolio/p09-evaluador-ideas-negocio
python -m pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Estado

Pieza de portfolio. Sirve para explorar ideas, no para tomar decisiones de inversion automaticamente.
