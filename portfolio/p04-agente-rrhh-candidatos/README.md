# P04 - Agente de criba de candidatos

Agente de portfolio para evaluar CVs y apoyar una primera criba de candidatos.

## Que hace

- Analiza el puesto y las competencias requeridas.
- Extrae texto de CVs en PDF.
- Indexa documentos localmente.
- Genera una preevaluacion estructurada por candidato.
- Sirve como apoyo a la seleccion inicial, no como decision final.

## Stack

- Streamlit
- Groq
- ChromaDB
- sentence-transformers
- PyMuPDF

## Como arrancarlo

1. Instala dependencias.
2. Crea `.env` a partir de `.env.example`.
3. Ejecuta `streamlit run app.py`.

## Estado

Pieza de portfolio funcional.
