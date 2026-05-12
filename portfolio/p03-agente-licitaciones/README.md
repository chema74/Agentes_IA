# P03 - Agente de evaluacion de licitaciones

Demo de portfolio para analizar pliegos de contratacion publica en PDF y preparar una primera lectura de viabilidad antes de decidir si presentarse o no.

## Que problema resuelve

Revisar un pliego de licitacion completo lleva horas. Este agente indexa el documento y genera un primer informe estructurado: score de viabilidad, riesgos detectados, requisitos clave y recomendacion. Sirve como primer filtro antes de dedicar recursos al analisis completo.

## A quien va dirigido

- Empresas y consultoras que participan en contratacion publica.
- Equipos comerciales que necesitan decidir rapidamente si una licitacion merece tiempo de analisis.

## Que hace

1. **Sube el pliego en PDF**: PyMuPDF extrae el texto y ChromaDB lo indexa localmente.
2. **Genera un informe inicial**: score de adecuacion (1-10), riesgos detectados, requisitos de solvencia, plazos clave y recomendacion (presentarse / no presentarse / revisar antes).
3. **Chat libre**: puedes hacer preguntas especificas sobre cualquier clausula o seccion del pliego con recuperacion de contexto RAG.

## Stack

- Streamlit
- Groq (LLama 3.3 70B)
- ChromaDB (base vectorial local)
- PyMuPDF (extraccion de texto)

## Instalacion

```bash
cd portfolio/p03-agente-licitaciones
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edita .env con tu GROQ_API_KEY
streamlit run app.py
```

## Limites

- Analiza el texto del pliego tal como esta: no interpreta graficos, tablas escaneadas ni anexos en imagen.
- El score y la recomendacion son orientativos. La decision final requiere revision humana experta.
- No reemplaza al equipo juridico o tecnico en la redaccion de la oferta.

## Estado

Prototipo de portfolio funcional orientado a la fase de primer filtro de licitaciones. Para un agente de extraccion de obligaciones contractuales con exportacion estructurada consulta el producto contract-obligations-agent del repositorio.
