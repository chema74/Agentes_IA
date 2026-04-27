# P05 - Base publica del motor RAG documental

Base de portfolio para consulta documental interna sobre PDFs de empresa.

## Que hace

- Sube documentacion interna en PDF.
- Indexa el contenido localmente con embeddings.
- Permite hacer preguntas en lenguaje natural.
- Recupera fragmentos relevantes y responde con contexto.

## Stack

- Groq
- ChromaDB
- sentence-transformers
- PyMuPDF
- Streamlit

## Instalacion

```bash
cd portfolio/p05-rag-documentacion-interna
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Estado

Pieza de portfolio solida para RAG documental interno, sin consolidar todavia el motor multi-dominio completo.
