# P09 - Evaluador de ideas de negocio

Demo de portfolio para valorar una idea de negocio con apoyo de IA y busqueda web.

## Que hace

Describe una idea de negocio y recibes un analisis estructurado con:

- puntuacion global de 1 a 10
- analisis por dimensiones: mercado, diferenciacion, viabilidad, ejecucion y timing
- fortalezas, debilidades, oportunidades y amenazas
- competidores clave
- modelo de negocio sugerido
- rango de inversion inicial
- plan de validacion
- consejo directo y accionable

## Stack

- Groq
- Tavily
- Streamlit

## Instalacion

```powershell
cd portfolio/p09-evaluador-ideas-negocio
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Limites

- Sirve para explorar ideas, no para tomar decisiones de inversion automaticamente.
- Las busquedas web pueden traer ruido o informacion parcial.
- El resultado debe contrastarse con validacion real de mercado.

## Estado

Pieza de portfolio funcional para discovery y pre-evaluacion. El valor esta en estructurar la conversacion y priorizar siguientes pasos, no en sustituir diligence real.
