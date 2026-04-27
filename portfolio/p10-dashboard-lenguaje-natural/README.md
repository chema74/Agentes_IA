# P10 - Dashboard con lenguaje natural

> Portfolio IA Aplicada - Jose Maria - Sevilla
> Stack: Groq - pandas - Plotly - Streamlit

## Que hace este proyecto

Esta version publica del agente final Dashboard con lenguaje natural permite:

- subir un archivo CSV o Excel,
- hacer preguntas en espanol sobre los datos,
- generar analisis y visualizaciones bajo demanda,
- ver el resultado en pantalla como grafico, tabla o valor.

No construye un dashboard persistente ni un modelo semantico completo. Su alcance actual es la exploracion asistida de datasets tabulares con lenguaje natural.

## Ejemplos de preguntas

- Cual fue el mes con mas ventas?
- Muestrame un grafico de barras por categoria
- Cual es el valor medio de la columna precio?
- Existe correlacion entre ventas e ingresos?
- Muestrame los 10 clientes con mas pedidos

## Instalacion

```bash
cd portfolio/p10-dashboard-lenguaje-natural
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

## Como funciona

```text
Usuario sube CSV/Excel
        ->
Streamlit carga el DataFrame con pandas
        ->
Usuario escribe una pregunta en espanol
        ->
Groq genera codigo Python de analisis
        ->
La app valida el codigo y lo ejecuta con restricciones basicas
        ->
Resultado: grafico Plotly / tabla / valor
```

## Limites operativos

- El analisis depende de codigo generado por un LLM.
- Conviene revisar los resultados antes de usarlos para decisiones importantes.
- Es preferible trabajar con datos no sensibles o anonimizar el archivo antes de subirlo.
- La app aplica validaciones basicas antes de ejecutar el codigo, pero no implementa una sandbox completa.

*Portfolio IA Aplicada - Jose Maria - Sevilla - 2026*
