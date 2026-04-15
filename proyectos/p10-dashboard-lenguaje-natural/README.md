# P10 · Dashboard con lenguaje natural

> **Portfolio IA Aplicada · José María · Sevilla**  
> Stack: Groq · pandas · Plotly · Streamlit

---

## Qué hace este proyecto

Esta versión pública del agente final **Dashboard con lenguaje natural** permite:

- subir un archivo CSV o Excel,
- hacer preguntas en español sobre los datos,
- generar análisis y visualizaciones bajo demanda,
- ver el resultado en pantalla como gráfico, tabla o valor.

No construye un dashboard persistente ni un modelo semántico completo. Su alcance actual es la **exploración asistida de datasets tabulares** con lenguaje natural.

---

## Ejemplos de preguntas

- *¿Cuál fue el mes con más ventas?*
- *Muéstrame un gráfico de barras por categoría*
- *¿Cuál es el valor medio de la columna precio?*
- *¿Existe correlación entre ventas e ingresos?*
- *Muéstrame los 10 clientes con más pedidos*

---

## Instalación

```bash
cd proyectos/p10-dashboard-lenguaje-natural
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Añadir GROQ_API_KEY en el archivo .env
python -m streamlit run app.py
```

---

## Cómo funciona

```text
Usuario sube CSV/Excel
        ↓
Streamlit carga el DataFrame con pandas
        ↓
Usuario escribe una pregunta en español
        ↓
Groq genera código Python de análisis
        ↓
La app valida el código y lo ejecuta con restricciones básicas
        ↓
Resultado: gráfico Plotly / tabla / valor
```

---

## Límites operativos

- El análisis depende de código generado por un LLM.
- Conviene revisar los resultados antes de usarlos para decisiones importantes.
- Es preferible trabajar con datos no sensibles o anonimizar el archivo antes de subirlo.
- La app aplica validaciones básicas antes de ejecutar el código, pero no implementa una sandbox completa.

---

*Portfolio IA Aplicada · José María · Sevilla · 2026*

