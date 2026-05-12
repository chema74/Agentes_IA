# P04 - Agente de criba de candidatos

Demo de portfolio para evaluar CVs en PDF y generar una primera preevaluacion estructurada por candidato, reduciendo el tiempo de criba inicial en procesos de seleccion.

## Que problema resuelve

Revisar manualmente decenas de CVs para una misma posicion consume horas. Este agente extrae el texto de cada CV, lo indexa localmente y genera un informe estructurado por candidato: adecuacion al perfil, competencias detectadas, puntos fuertes, gaps y una recomendacion de siguiente paso. Sirve como apoyo a la criba inicial, no como decision final.

## Que hace

- Analiza el perfil del puesto y las competencias requeridas.
- Extrae texto de los CVs en PDF con PyMuPDF.
- Indexa los documentos localmente con ChromaDB y embeddings.
- Genera una preevaluacion estructurada por candidato con score y recomendacion.
- Permite comparar candidatos entre si para facilitar la seleccion.

## Stack

- Streamlit
- Groq (LLama 3.3 70B)
- ChromaDB (base vectorial local)
- sentence-transformers (embeddings)
- PyMuPDF (extraccion de texto)

## Instalacion

```bash
cd portfolio/p04-agente-rrhh-candidatos
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edita .env con tu GROQ_API_KEY
streamlit run app.py
```

## Limites

- Analiza el texto extraido del CV: no interpreta maquetacion visual ni tablas escaneadas.
- La preevaluacion es orientativa. La decision de avanzar a entrevista es siempre del equipo de seleccion.
- No emite juicios sobre caracteristicas personales protegidas.
- Usar con datos anonimizados o de prueba en entornos de demo.

## Estado

Prototipo de portfolio funcional orientado a la fase de criba inicial. Para un modulo de seleccion con integracion en ATS y governance de equidad en seleccion consulta el repositorio de productos.
