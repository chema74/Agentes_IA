# P07 - Chatbot de atencion al cliente

Chatbot RAG para responder preguntas de clientes usando documentacion propia: catalogo, preguntas frecuentes, politicas, condiciones y soporte.

## Que hace

- Permite subir PDFs de conocimiento interno.
- Indexa los documentos localmente con ChromaDB.
- Recupera fragmentos relevantes.
- Responde con base en la documentacion cargada.
- Si no encuentra suficiente evidencia, propone escalar a una persona.

## Stack

- Streamlit
- Groq
- ChromaDB
- sentence-transformers
- PyMuPDF

## Ejecucion

1. Instala dependencias.
2. Crea `.env` a partir de `.env.example`.
3. Anade la API key de Groq.
4. Lanza `python -m streamlit run app.py`.

## Estado

Pieza de portfolio en desarrollo.
