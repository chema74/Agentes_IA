# P08 Â· Consultor RAG de Normativa de Comercio Internacional

> **Portfolio IA Aplicada â€” JosÃ© MarÃ­a Â· Sevilla**  
> Stack: Groq Â· ChromaDB Â· sentence-transformers Â· PyMuPDF Â· Streamlit  
> Coste: **GRATUITO**

## Â¿QuÃ© hace?

Carga guÃ­as ICEX, acuerdos comerciales UE y normativa aduanera en PDF.  
Pregunta sobre aranceles, requisitos de origen, documentaciÃ³n y barreras.  
Responde con fuente citada, adaptando la respuesta al contexto paÃ­s origen/destino/producto configurado.

**Fuentes recomendadas:** GuÃ­as de mercado ICEX Â· Acuerdos UE (EUR-Lex) Â· Reglamentos aduaneros

## InstalaciÃ³n

```bash
pip install -r requirements.txt
copy .env.example .env   # aÃ±adir GROQ_API_KEY
python -m streamlit run app.py
```

---
*Portfolio IA Aplicada Â· JosÃ© MarÃ­a Â· Sevilla*
