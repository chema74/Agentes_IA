# P03 - Agente de evaluacion de licitaciones

Agente de portfolio para analizar pliegos en PDF y preparar una primera lectura de viabilidad.

## Que hace

- Indexa el contenido del pliego en ChromaDB local.
- Genera un analisis estructurado con score, riesgos y recomendacion.
- Permite chat libre sobre el documento con recuperacion de contexto.

## Stack

- Streamlit
- Groq
- ChromaDB
- PyMuPDF

## Requisitos

- Python 3.11
- `GROQ_API_KEY`

## Como arrancarlo

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## Estado

Pieza de portfolio funcional, orientada a demo.
