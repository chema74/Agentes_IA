# P08 - RAG de normativa de comercio internacional

Agente de portfolio para consultar normativa, guias y documentos de comercio internacional con apoyo de IA.

## Que hace

- Carga PDFs de normativa y documentacion de comercio exterior.
- Permite preguntar por aranceles, origen, documentacion y barreras.
- Responde con apoyo en los fragmentos recuperados.
- Anade contexto de pais origen, destino y producto para enfocar la consulta.

## Fuentes recomendadas

- Guias de mercado ICEX
- Acuerdos UE y EUR-Lex
- Reglamentos aduaneros
- Documentacion operativa de exportacion

## Instalacion

```powershell
cd portfolio/p08-rag-normativa-comercio
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Limites

- La app responde solo sobre la normativa cargada.
- La normativa puede quedar desactualizada y debe revisarse contra la fuente oficial.
- No es un dictamen juridico ni una asesoria formal de cumplimiento.

## Estado

Demo documental orientativa, util para discovery y apoyo inicial en comercio exterior. Todavia no sustituye un flujo regulatorio serio con fuentes oficiales versionadas.
