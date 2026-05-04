# P06 - Revisor de contratos legales

Version publica de portfolio para revisar contratos y otros documentos legales con ayuda de RAG local y un LLM.

## Que hace

- Sube contratos y documentos legales en PDF.
- Indexa el contenido localmente para consulta posterior.
- Permite preguntar por clausulas, obligaciones, plazos, penalizaciones o riesgos detectables en el texto.
- Devuelve respuestas apoyadas en fragmentos recuperados del propio documento.

Su funcion es asistir la revision documental, no sustituir revision juridica profesional.

## Ejemplos de preguntas

- Cuales son las clausulas mas importantes de este contrato?
- Que riesgos o clausulas sensibles detectas en el texto?
- Cuales son las obligaciones de cada parte?
- Que plazos y fechas clave aparecen en el documento?
- Que condiciones de rescision o penalizacion se recogen?

## Stack

- Groq
- ChromaDB
- sentence-transformers
- PyMuPDF
- Streamlit

## Instalacion

```powershell
cd portfolio/p06-rag-contratos-legales
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

Primera ejecucion: se descarga el modelo `all-MiniLM-L6-v2` una sola vez.

## Limites

- Las respuestas dependen del texto recuperado y del modelo.
- Conviene revisar siempre el documento original.
- La app envia al modelo solo los fragmentos relevantes recuperados para responder.
- No emite dictamenes legales ni sustituye asesoramiento juridico.

## Estado

Pieza de portfolio funcional para revision asistida de contratos. Debe leerse como demo documental seria, no como sustituto del producto legal mas maduro de `products/`.
