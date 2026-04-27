# P08 - Consultor RAG de normativa de comercio internacional

Agente de portfolio para consultar normativa, guias y documentos de comercio internacional con apoyo de IA.

## Que hace

- Carga guias ICEX, acuerdos comerciales UE y normativa aduanera en PDF.
- Permite preguntar por aranceles, origen, documentacion y barreras.
- Responde con fuente citada y contexto de pais origen, destino o producto.

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

## Estado

Demo documental orientativa, no dictamen juridico ni asesoria de cumplimiento.
