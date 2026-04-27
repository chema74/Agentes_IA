# P02 · Executive Agent Pro. 

Agente de Inteligencia Artificial de alto rendimiento diseñado para la toma de decisiones ejecutivas. Este sistema no solo responde; **piensa, busca y analiza**.

## 🌟 Características de Nivel Experto
- **Reasoning Engine:** Utiliza Llama-3.3 sobre Groq para decisiones en milisegundos.
- **Dynamic Tool Calling:** El agente decide autónomamente cuándo necesita internet (Tavily) o cuándo consultar tus archivos privados (RAG).
- **Streaming UI:** Experiencia de usuario fluida con respuestas en tiempo real.
- **Contextual PDF RAG:** Manejo inteligente de documentos largos mediante fragmentación semántica.

## 🛠️ Stack Tecnológico
- **Core:** Groq Cloud (Inferencia de ultra baja latencia).
- **Search:** Tavily AI (Búsqueda optimizada para LLMs).
- **Processing:** PyMuPDF & LangChain.
- **Frontend:** Streamlit con Custom CSS.

## 🚀 Despliegue Rápido
1. Clona el repositorio.
2. Crea un archivo `.env` con `GROQ_API_KEY` y `TAVILY_API_KEY`.
3. Ejecuta: `pip install -r requirements.txt && streamlit run app.py`.

---
*Portfolio IA Aplicada · José María · Sevilla 2026*