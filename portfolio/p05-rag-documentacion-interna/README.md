# P05 - RAG de documentacion interna

Base publica de portfolio para consulta documental interna sobre PDFs de empresa.

## Que hace

- Sube documentacion interna en PDF.
- Extrae texto y lo indexa localmente con ChromaDB.
- Permite hacer preguntas en lenguaje natural.
- Recupera fragmentos relevantes y responde con contexto.
- Muestra fuentes y paginas cuando hay respaldo documental.

## Stack

- Groq
- ChromaDB
- sentence-transformers
- PyMuPDF
- Streamlit

## Instalacion

```powershell
cd portfolio/p05-rag-documentacion-interna
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Uso recomendado

Documentos utiles para demo:

- manual de empleado
- politicas internas
- procedimientos operativos
- FAQs
- organigramas
- guias de producto

## Limites

- La indexacion es local, pero la respuesta se genera con Groq a partir de los fragmentos recuperados.
- No sustituye la lectura del documento original.
- Funciona mejor con PDFs con texto seleccionable.

## Estado

Pieza de portfolio funcional y estable. Buena base publica para RAG documental interno, aunque todavia no pretende cubrir un motor multi-dominio completo ni flujos enterprise.
