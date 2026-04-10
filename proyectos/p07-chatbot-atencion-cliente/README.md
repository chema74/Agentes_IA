# P08 · Chatbot de Atención al Cliente sobre Base de Conocimiento Propia

> Estado: En desarrollo

Chatbot RAG para responder preguntas de clientes usando documentación propia:
catálogo, preguntas frecuentes, políticas, condiciones y soporte.

## Qué hace
- Permite subir PDFs de conocimiento interno
- Indexa los documentos localmente con ChromaDB
- Recupera fragmentos relevantes
- Responde con base en la documentación cargada
- Si no encuentra suficiente evidencia, indica que debe escalarse a un agente humano

## Stack
- Streamlit
- Groq
- ChromaDB
- sentence-transformers
- PyMuPDF

## Ejecución
1. Instalar dependencias:
   python -m pip install -r requirements.txt

2. Crear entorno de variables:
   copy .env.example .env

3. Añadir la API key de Groq en `.env`

4. Lanzar:
   python -m streamlit run app.py