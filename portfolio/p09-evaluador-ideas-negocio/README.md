# P09 - Evaluador de Ideas de Negocio con IA

> Portfolio IA Aplicada - Jose Maria - Sevilla  
> Stack: Groq - Tavily - Streamlit  
> Coste: Gratuito

## Que hace este proyecto

Describe tu idea de negocio y en pocos segundos recibes un analisis estructurado:

- puntuacion global 1-10 con veredicto claro,
- analisis por 5 dimensiones: mercado, diferenciacion, viabilidad, ejecucion y timing,
- DAFO completo,
- identificacion de competidores clave,
- modelo de negocio sugerido con estimacion de inversion,
- plan de validacion de 5 pasos,
- consejo directo sin adornos innecesarios.

## Instalacion

```bash
cd portfolio/p09-evaluador-ideas-negocio
python -m pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Notas

- Usa `GROQ_API_KEY` y `TAVILY_API_KEY`.
- Es una demo de evaluacion orientativa, no una decision de inversion automatica.

