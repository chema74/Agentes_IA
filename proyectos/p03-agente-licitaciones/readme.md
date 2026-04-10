# P03 - Agente de Evaluacion y Preparacion de Licitaciones

Stack: Streamlit + Groq + ChromaDB + PyMuPDF

## Que hace

Subes un pliego en PDF y la app:
- indexa el contenido en ChromaDB local,
- genera un analisis de viabilidad (JSON estructurado con score, riesgos y recomendacion),
- permite chat libre sobre el pliego con recuperacion de contexto desde embeddings.

## Requisitos

- Python 3.11 (recomendado: 3.11.9)
- Clave `GROQ_API_KEY`

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Despues, edita `.env` y completa:

```bash
GROQ_API_KEY=tu_clave_real
```

## Ejecucion

```bash
streamlit run app.py
```

## Comportamiento real y limites

- El indice vectorial se guarda en `./chroma_db_p03`.
- Tras reiniciar la app, los embeddings pueden seguir disponibles para consulta.
- El texto completo del PDF no se reconstruye automaticamente desde chunks solapados.
- Para un analisis fiel de viabilidad tras reinicio, vuelve a subir el PDF.
- El analisis usa un extracto maximo de `5000` caracteres del pliego (`MAX_TEXTO_ANALISIS`).

## Troubleshooting rapido

- Error de API: revisa que `GROQ_API_KEY` exista en `.env`.
- Error de Chroma: elimina `chroma_db_p03` y vuelve a indexar el PDF.
- Entorno sin Python activo (pyenv): fija version local/global antes de instalar dependencias.
