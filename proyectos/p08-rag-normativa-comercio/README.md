# P09 · Consultor RAG de Normativa de Comercio Internacional

> **Portfolio IA Aplicada — José María · Sevilla**  
> Stack: Groq · ChromaDB · sentence-transformers · PyMuPDF · Streamlit  
> Coste: **GRATUITO**

## ¿Qué hace?

Carga guías ICEX, acuerdos comerciales UE y normativa aduanera en PDF.  
Pregunta sobre aranceles, requisitos de origen, documentación y barreras.  
Responde con fuente citada, adaptando la respuesta al contexto país origen/destino/producto configurado.

**Fuentes recomendadas:** Guías de mercado ICEX · Acuerdos UE (EUR-Lex) · Reglamentos aduaneros

## Instalación

```bash
pip install -r requirements.txt
copy .env.example .env   # añadir GROQ_API_KEY
python -m streamlit run app.py
```

---
*Portfolio IA Aplicada · José María · Sevilla*