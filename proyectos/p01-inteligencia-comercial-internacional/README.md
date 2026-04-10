# P01 · Inteligencia comercial internacional

> **Portfolio IA Aplicada · Txema Rios · Sevilla**  
> Stack: Groq · Tavily · Streamlit · Pydantic · pandas

---

## Que hace hoy este proyecto

Esta es la **base publica actual** del agente final **Agente de inteligencia comercial internacional**.

Su funcion actual es ayudar a comparar paises y mercados para apoyar decisiones comerciales internacionales mediante:

- busqueda web asistida sobre senales relevantes de mercado,
- analisis estructurado por dimensiones,
- comparacion entre paises,
- ranking orientativo de mercados,
- historial basico de resultados.

No se presenta como un sistema formal de rating pais, una due diligence completa ni una asesoria juridica o regulatoria.

---

## Flujo principal

1. Seleccionar uno o varios paises a comparar.
2. Elegir sector y tipo de empresa.
3. Recuperar contexto con busqueda web y analisis asistido por modelo.
4. Mostrar resumen ejecutivo, senales por dimension y comparativa orientativa.
5. Revisar ranking o historial cuando existan datos previos.

---

## Que entrega

- resumen ejecutivo por pais,
- senales por dimension para apoyar la comparacion,
- comparativa entre dos mercados,
- ranking orientativo de varios paises,
- panel historico con resultados guardados por la aplicacion.

---

## Limites importantes

- Los resultados son **orientativos** y no equivalen a una evaluacion soberana formal.
- La app se apoya en busqueda web y analisis asistido por LLM; conviene revisar el resultado antes de usarlo para decisiones relevantes.
- No promete exhaustividad geoeconomica, regulatoria o geopolítica total.
- No sustituye due diligence comercial, legal o de cumplimiento.
- La version publica actual cubre bien el caso de uso de comparacion y priorizacion de mercados, pero no representa todavia toda la consolidacion futura del agente final.

---

## Posicionamiento publico

P01 debe leerse como una herramienta de apoyo para **estructurar senales comerciales internacionales** y comparar mercados de forma agil.

Ese posicionamiento es consistente con el estado actual del proyecto. No conviene venderlo como:

- rating pais formal,
- motor geopolítico exhaustivo,
- auditoria regulatoria completa,
- garantia de entrada exitosa a mercado.

---

## Instalacion y ejecucion local

```bash
cd proyectos/p01-inteligencia-comercial-internacional
pyenv local 3.11.9
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
# Edita .env con tus claves API
streamlit run app/streamlit_app.py
```

---

## Ejecucion de tests

```bash
cd proyectos/p01-inteligencia-comercial-internacional
pyenv local 3.11.9
pytest -q
```

La suite usa `pytest.ini` para fijar `--basetemp=.pytest_tmp` y evitar problemas de permisos con el directorio temporal global de Windows.

---

## Variables de entorno

```env
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
```

- `GROQ_API_KEY`: analisis y generacion narrativa.
- `TAVILY_API_KEY`: busqueda web para recuperar contexto reciente.

---

## Por que encaja en el portfolio final

P01 ya puede sostenerse como base publica actual del agente final **Agente de inteligencia comercial internacional** porque su caso de uso central es claro y defendible: comparar mercados, priorizar paises y estructurar senales para decisiones comerciales internacionales.

Las futuras consolidaciones con otros proyectos fuente podran ampliar cobertura y profundidad, pero no son necesarias para que esta base publica sea creible hoy.

---

*Portfolio IA Aplicada · Txema Rios · Sevilla · 2026*
