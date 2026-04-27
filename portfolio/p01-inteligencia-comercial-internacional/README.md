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

## Interpretacion del score orientativo

El indicador principal visible al usuario es un **indice orientativo de riesgo** (internamente `score_total`):

- mide una estimacion comparativa de senales de riesgo y oportunidad sin presentarse como una escala fija o certificada,
- **menor score = mejor posicion relativa** para priorizacion comparativa,
- no es un rating certificado ni un veredicto de entrada a mercado.

Uso apropiado:

- priorizar mercados de forma exploratoria,
- ordenar candidatos para analisis posterior.

Uso no apropiado:

- sustituir due diligence legal, regulatoria o de cumplimiento,
- tomar decisiones finales de inversion o entrada sin validacion profesional adicional.

Advertencia metodologica:

- si cambian pesos, dimensiones o metodologia, la comparabilidad historica puede verse afectada.

---

## Alcance del modo demo

El modo demo valida que:

- el flujo de comparacion y ranking funciona de extremo a extremo sin APIs reales,
- los paises soportados en el catalogo demo se procesan de forma consistente,
- los paises fuera de catalogo muestran mensajes claros,
- los rankings generados se guardan en el historico local para el dashboard.

El modo demo no valida que:

- los proveedores reales (Groq/Tavily) respondan correctamente,
- los prompts y respuestas en produccion sean estables frente a variaciones reales,
- el rendimiento y los limites de cuota de APIs en escenarios reales sean suficientes.

Por tanto, el modo demo no sustituye una validacion posterior con APIs reales.

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
cd portfolio/p01-inteligencia-comercial-internacional
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
cd portfolio/p01-inteligencia-comercial-internacional
pyenv local 3.11.9
pytest -q
```

La suite usa `pytest.ini` para fijar `--basetemp=.pytest_tmp` y evitar problemas de permisos con el directorio temporal global de Windows.

---

## Checklist manual demo

1. Ejecutar un ranking demo con paises soportados (ej: Mexico, Alemania) y confirmar que se genera tabla.
2. Ejecutar un ranking demo con paises no soportados (ej: Francia, Argentina) y confirmar mensaje explicito de catalogo demo.
3. Ejecutar un ranking mixto (ej: Mexico, Francia, Alemania) y confirmar que omite no soportados y continua con soportados.
4. Confirmar que tras un ranking valido se crea un run en `history/` con `manifest.json` y `ranking.json`.
5. Abrir dashboard y verificar que aparecen filas historicas del ranking guardado.

---

## Variables de entorno

```env
APP_MODE=demo
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
```

- `APP_MODE`: controla si la app arranca en `demo` o `production`.
- `GROQ_API_KEY`: analisis y generacion narrativa.
- `TAVILY_API_KEY`: busqueda web para recuperar contexto reciente.

## Configuracion desacoplada

- Los pesos configurables viven en `config/weights.yaml`.
- Si el YAML falta o es invalido, la app usa defaults seguros compatibles con la version actual.
- El modo `demo` no depende de APIs reales; `production` valida las claves necesarias al arrancar.

## Deploy minimo en Streamlit Cloud

- Entry point: `portfolio/p01-inteligencia-comercial-internacional/app/streamlit_app.py`
- Requirements file: `portfolio/p01-inteligencia-comercial-internacional/requirements.txt`
- Secrets recomendados: mismo contenido que en `.streamlit/secrets.toml.example`

```toml
APP_MODE="production"
GROQ_API_KEY="gsk_..."
TAVILY_API_KEY="tvly-..."
APP_STORAGE_DIR="/tmp/p01-inteligencia-comercial-internacional"
```

- `APP_STORAGE_DIR` mueve cache, logs e historico a un filesystem efimero y escribible en Cloud.
- En local, si quieres simular el deploy, copia ese contenido a `.streamlit/secrets.toml`.

---

## Por que encaja en el portfolio final

P01 ya puede sostenerse como base publica actual del agente final **Agente de inteligencia comercial internacional** porque su caso de uso central es claro y defendible: comparar mercados, priorizar paises y estructurar senales para decisiones comerciales internacionales.

Las futuras consolidaciones con otros proyectos fuente podran ampliar cobertura y profundidad, pero no son necesarias para que esta base publica sea creible hoy.

---

*Portfolio IA Aplicada · Txema Rios · Sevilla · 2026*
