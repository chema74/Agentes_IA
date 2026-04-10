# P05 · Base pública actual del motor RAG corporativo multi-dominio

> **Portfolio IA Aplicada · José María · Sevilla**  
> Stack: Groq · ChromaDB · sentence-transformers · Streamlit  
> Coste: **gratuito** salvo la llamada al modelo

---

## Qué hace este proyecto

Esta versión pública de **P05** actúa como base actual del agente final **Motor RAG corporativo multi-dominio**.

Hoy cubre un caso de uso concreto y defendible: **consulta documental interna con RAG sobre PDFs de empresa**.

Permite:

- subir documentación interna en PDF,
- indexarla localmente con embeddings,
- hacer preguntas en lenguaje natural,
- recuperar fragmentos relevantes,
- obtener respuestas asistidas a partir del contexto recuperado.

No representa todavía la consolidación completa del motor multi-dominio ni integra por sí solo todas las capacidades asociadas a otros proyectos fuente.

---

## Casos de uso

- *¿Cuántos días de vacaciones tengo al año?*
- *¿Cuál es el proceso para solicitar una baja médica?*
- *¿A quién reporto una incidencia de IT?*
- *Resume los valores y la misión de la empresa.*
- *¿Qué herramientas usa el departamento de ventas?*

---

## Cómo funciona

```text
PDFs de la empresa
      ↓
PyMuPDF extrae el texto página a página
      ↓
El texto se divide en fragmentos y se vectoriza localmente
      ↓
ChromaDB guarda los embeddings en disco
      ↓
El usuario hace una pregunta
      ↓
La app recupera los fragmentos más relevantes
      ↓
Groq genera una respuesta apoyada en esos fragmentos
      ↓
Streamlit muestra la respuesta y las fuentes consultadas
```

---

## Instalación

```bash
cd proyectos/p05-rag-documentacion-interna
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Añadir GROQ_API_KEY en el archivo .env
python -m streamlit run app.py
```

**Nota:** en la primera ejecución, `sentence-transformers` descarga el modelo `all-MiniLM-L6-v2` (~90 MB). Solo ocurre una vez.

---

## Límites operativos

- La indexación, los embeddings y la base vectorial se gestionan localmente.
- Para responder, la app envía al modelo la pregunta del usuario y los fragmentos recuperados como contexto.
- La respuesta intenta apoyarse en los documentos indexados, pero no conviene asumir exhaustividad total ni ausencia de errores.
- Es una base pública sólida para RAG documental interno, no la consolidación completa del motor RAG corporativo multi-dominio.

---

## Estructura del proyecto

```text
p05-rag-documentacion-interna/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

*Portfolio IA Aplicada · José María · Sevilla · 2026*
