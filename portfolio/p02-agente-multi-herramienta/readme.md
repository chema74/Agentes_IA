# P02 - Agente multi-herramienta con tool calling y RAG

Demo de portfolio que muestra como un agente LLM decide en tiempo real que herramienta usar para responder: busqueda web, analisis de documento o conocimiento propio.

## Que problema resuelve

Un profesional necesita respuestas que combinan informacion reciente de internet con contenido de un documento interno. En lugar de buscar a mano en varias fuentes, describe lo que necesita en lenguaje natural y el agente decide que fuente consultar, extrae lo relevante y sintetiza la respuesta.

## Que hace

- **Tool calling real**: el modelo decide autonomamente si buscar en la web, analizar el PDF cargado o responder directamente.
- **Busqueda web**: Tavily recupera informacion actualizada del mercado o de cualquier tema.
- **RAG sobre documento**: PyMuPDF extrae el texto del PDF y el agente busca el fragmento mas relevante para la pregunta.
- **Memoria de sesion**: mantiene el hilo de la conversacion para preguntas de seguimiento.
- **Historial persistente**: guarda y carga sesiones anteriores.
- **Exportacion**: genera informe Word de la conversacion.

## En que se diferencia de p05, p06 y p07

p05, p06 y p07 son RAGs especializados con ChromaDB y embeddings locales. Este agente usa tool calling nativo de Groq: el modelo elige herramienta, ejecuta, recibe el resultado y sintetiza. Es la pieza de portfolio que ilustra el patron agente con herramientas, no el patron RAG.

## Stack

- Groq (LLama 3.3 70B con tool calling)
- Tavily (busqueda web)
- Streamlit
- PyMuPDF (extraccion de texto PDF)
- python-docx (exportacion Word)

## Instalacion

```bash
cd portfolio/p02-agente-multi-herramienta
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edita .env con tus claves GROQ_API_KEY y TAVILY_API_KEY
streamlit run app.py
```

## Limites

- Orientado a demo. Para un asistente ejecutivo con governance y auditoria consulta los productos del repositorio.
- La busqueda web depende de la cuota de Tavily.
- El analisis de PDF funciona sobre texto seleccionable, no sobre PDFs escaneados.

## Estado

Pieza de portfolio funcional que ilustra el patron tool calling con decision autonoma de herramienta.
