# P08 - Consultor RAG de Normativa de Comercio Internacional

> Portfolio IA Aplicada - Jose Maria - Sevilla
> Stack: Groq - ChromaDB - sentence-transformers - PyMuPDF - Streamlit
> Coste: Gratuito

## Que hace

- Carga guias ICEX, acuerdos comerciales UE y normativa aduanera en PDF.
- Pregunta sobre aranceles, requisitos de origen, documentacion y barreras.
- Responde con fuente citada y adapta la respuesta al contexto pais origen/destino/producto configurado.

## Fuentes recomendadas

- Guias de mercado ICEX
- Acuerdos UE (EUR-Lex)
- Reglamentos aduaneros

## Instalacion

```bash
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Nota

Es una demo documental orientativa, no un dictamen juridico ni una asesoria de cumplimiento.

