# P05 - Base publica actual del motor RAG corporativo multi-dominio

> Portfolio IA Aplicada - Txema Rios - Sevilla
> Stack: Groq - ChromaDB - sentence-transformers - Streamlit
> Coste: gratuito salvo la llamada al modelo

## Que hace este proyecto

Esta version publica de P05 actua como base actual del agente final Motor RAG corporativo multi-dominio.

Hoy cubre un caso de uso concreto y defendible: consulta documental interna con RAG sobre PDFs de empresa.

Permite:

- subir documentacion interna en PDF,
- indexarla localmente con embeddings,
- hacer preguntas en lenguaje natural,
- recuperar fragmentos relevantes,
- obtener respuestas asistidas a partir del contexto recuperado.

No representa todavia la consolidacion completa del motor multi-dominio ni integra por si solo todas las capacidades asociadas a otros proyectos fuente.

## Casos de uso

- Cuantos dias de vacaciones tengo al ano?
- Cual es el proceso para solicitar una baja medica?
- A quien reporto una incidencia de IT?
- Resume los valores y la mision de la empresa.
- Que herramientas usa el departamento de ventas?

## Como funciona

```text
PDFs de la empresa
      ->
PyMuPDF extrae el texto pagina a pagina
      ->
El texto se divide en fragmentos y se vectoriza localmente
      ->
ChromaDB guarda los embeddings en disco
      ->
El usuario hace una pregunta
      ->
La app recupera los fragmentos mas relevantes
      ->
Groq genera una respuesta apoyandose en esos fragmentos
      ->
Streamlit muestra la respuesta y las fuentes consultadas
```

## Instalacion

```bash
cd portfolio/p05-rag-documentacion-interna
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

Nota: en la primera ejecucion, `sentence-transformers` descarga el modelo `all-MiniLM-L6-v2` (~90 MB). Solo ocurre una vez.

## Limites operativos

- La indexacion, los embeddings y la base vectorial se gestionan localmente.
- Para responder, la app envia al modelo la pregunta del usuario y los fragmentos recuperados como contexto.
- La respuesta intenta apoyarse en los documentos indexados, pero no conviene asumir exhaustividad total ni ausencia de errores.
- Es una base publica solida para RAG documental interno, no la consolidacion completa del motor RAG corporativo multi-dominio.

## Estructura del proyecto

```text
portfolio/p05-rag-documentacion-interna/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*Portfolio IA Aplicada - Txema Rios - Sevilla - 2026*
