# P07 - Chatbot de Atencion al Cliente sobre Base de Conocimiento Propia

> Estado: En desarrollo

Chatbot RAG para responder preguntas de clientes usando documentacion propia:
catalogo, preguntas frecuentes, politicas, condiciones y soporte.

## Que hace

- Permite subir PDFs de conocimiento interno
- Indexa los documentos localmente con ChromaDB
- Recupera fragmentos relevantes
- Responde con base en la documentacion cargada
- Si no encuentra suficiente evidencia, indica que debe escalarse a un agente humano

## Stack

- Streamlit
- Groq
- ChromaDB
- sentence-transformers
- PyMuPDF

## Ejecucion

1. Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

2. Crear entorno de variables:

```bash
copy .env.example .env
```

3. Anadir la API key de Groq en `.env`

4. Lanzar:

```bash
python -m streamlit run app.py
```

