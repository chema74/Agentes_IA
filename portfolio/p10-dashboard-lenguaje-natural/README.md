# P10 - Dashboard con lenguaje natural

Dashboard de portfolio para explorar datasets tabulares mediante preguntas en lenguaje natural.

## Que hace

- Sube un CSV o Excel.
- Permite hacer preguntas en espanol sobre los datos.
- Genera analisis y visualizaciones bajo demanda.
- Muestra el resultado como grafico, tabla o valor.
- Aplica validaciones basicas antes de ejecutar el codigo generado por el LLM.

## Stack

- Groq
- pandas
- Plotly
- Streamlit

## Ejemplos de preguntas

- Cual fue el mes con mas ventas?
- Muestrame un grafico de barras por categoria.
- Cual es el valor medio de la columna precio?
- Existe correlacion entre ventas e ingresos?
- Muestrame los 10 clientes con mas pedidos.

## Instalacion

```powershell
cd portfolio/p10-dashboard-lenguaje-natural
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Limites

- El analisis depende de codigo generado por un LLM.
- Conviene revisar los resultados antes de usarlos para decisiones importantes.
- La app tiene guardrails basicos, no una sandbox completa.

## Estado

Demo de exploracion tabular con una base razonable para evolucionar. Es util para analisis guiado y presentaciones, pero no debe tratarse como entorno seguro multiusuario.
