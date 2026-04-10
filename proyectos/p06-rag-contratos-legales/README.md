# P07 · Revisor de contratos legales

> **Portfolio IA Aplicada · José María · Sevilla**  
> Stack: Groq · ChromaDB · sentence-transformers · PyMuPDF · Streamlit  
> Coste: **gratuito** salvo la clave de acceso a Groq

## Qué hace este proyecto

Esta versión pública del agente final **Revisor de contratos legales** permite:

- subir contratos y otros documentos legales en PDF,
- indexarlos localmente para consultar el contenido,
- hacer preguntas sobre cláusulas, obligaciones, plazos, penalizaciones o riesgos detectables en el texto,
- obtener respuestas con referencia a los fragmentos del documento recuperados.

Su función es **asistir la revisión documental**, no sustituir la revisión jurídica profesional.

## Ejemplos de preguntas

- *¿Cuáles son las cláusulas más importantes de este contrato?*
- *¿Qué riesgos o cláusulas sensibles detectas en el texto?*
- *¿Cuáles son las obligaciones de cada parte?*
- *¿Qué plazos y fechas clave aparecen en el documento?*
- *¿Qué condiciones de rescisión o penalización se recogen?*

## Instalación

```bash
cd proyectos/p07-rag-contratos-legales
pip install -r requirements.txt
copy .env.example .env
# Añadir GROQ_API_KEY en el archivo .env
python -m streamlit run app.py
```

**Primera ejecución:** se descarga el modelo `all-MiniLM-L6-v2` (~90 MB, solo una vez).

## Cómo funciona

```text
Usuario sube uno o varios PDFs
        ↓
La app extrae texto y genera embeddings locales con ChromaDB
        ↓
El usuario formula una pregunta sobre el documento
        ↓
La app recupera los fragmentos más relevantes
        ↓
Groq responde a partir de esos fragmentos
        ↓
Se muestra una respuesta asistida con referencia útil al documento
```

## Límites operativos

- Las respuestas dependen del texto recuperado y del modelo LLM.
- Conviene revisar siempre el documento original y validar los hallazgos antes de tomar decisiones jurídicas.
- La app indexa los documentos localmente, pero envía al modelo los fragmentos relevantes recuperados para poder responder.
- No sustituye asesoramiento legal profesional ni emite dictámenes jurídicos.

---

*Portfolio IA Aplicada · José María · Sevilla · 2026*
