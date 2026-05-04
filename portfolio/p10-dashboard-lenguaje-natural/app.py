"""
P10 - Dashboard con lenguaje natural
===================================
Autor: Jose Maria
Stack: Groq - pandas - Plotly - Streamlit

Como funciona:
1. El usuario sube un CSV o Excel.
2. Escribe una pregunta en espanol sobre los datos.
3. Groq genera codigo Python de analisis.
4. La app valida el codigo y lo ejecuta con restricciones basicas.
5. Se muestra el resultado como grafico, tabla o valor.
"""
import ast
import json
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

ALLOWED_BUILTINS = {
    "len": len,
    "sum": sum,
    "min": min,
    "max": max,
    "round": round,
    "sorted": sorted,
    "abs": abs,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "float": float,
    "int": int,
    "str": str,
    "bool": bool,
    "range": range,
}

MAX_CODE_CHARS = 4000
MAX_CODE_LINES = 80
MAX_AST_NODES = 500

PATRONES_BLOQUEADOS = {
    "import ": "No se permiten importaciones dinamicas.",
    "from ": "No se permiten importaciones dinamicas.",
    "__": "No se permiten accesos especiales de Python.",
    "open(": "No se permite acceder a archivos locales.",
    "exec(": "No se permite ejecutar codigo adicional.",
    "eval(": "No se permite evaluar expresiones arbitrarias.",
    "compile(": "No se permite compilar codigo dinamicamente.",
    "globals(": "No se permite acceder al entorno global.",
    "locals(": "No se permite acceder al entorno local.",
    "input(": "No se permite pedir entrada adicional.",
    "quit(": "No se permite finalizar el proceso.",
    "exit(": "No se permite finalizar el proceso.",
    "os.": "No se permite acceder al sistema operativo.",
    "sys.": "No se permite acceder al sistema.",
    "subprocess": "No se permite lanzar procesos.",
    "shutil": "No se permite operar sobre archivos.",
    "pathlib": "No se permite operar sobre rutas.",
    "socket": "No se permite acceso de red.",
    "requests": "No se permite acceso HTTP.",
    "getattr(": "No se permite reflexion dinamica.",
    "setattr(": "No se permite mutar atributos dinamicamente.",
    "delattr(": "No se permite borrar atributos dinamicamente.",
}

NOMBRES_BLOQUEADOS = {
    "open",
    "exec",
    "eval",
    "compile",
    "globals",
    "locals",
    "input",
    "quit",
    "exit",
    "__import__",
    "os",
    "sys",
    "subprocess",
    "pathlib",
    "shutil",
    "socket",
    "requests",
    "getattr",
    "setattr",
    "delattr",
}

NODOS_BLOQUEADOS = (
    ast.Try,
    ast.Raise,
    ast.With,
    ast.AsyncWith,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
    ast.Delete,
    ast.Global,
    ast.Nonlocal,
    ast.Await,
    ast.Yield,
    ast.YieldFrom,
)

ATRIBUTOS_BLOQUEADOS = {
    "__class__",
    "__dict__",
    "__mro__",
    "__subclasses__",
    "to_pickle",
    "to_parquet",
    "to_feather",
    "to_hdf",
    "to_sql",
}


st.set_page_config(
    page_title="Dashboard con lenguaje natural",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,300&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family:'DM Sans',sans-serif; background:#0c0c10; color:#e4e2dc; }
.stApp { background:#0c0c10; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:2rem; padding-bottom:2rem; max-width:1200px; }

.app-tag { font-family:'DM Mono',monospace; font-size:.65rem; letter-spacing:.2em; text-transform:uppercase; color:#d4a84b; margin-bottom:.75rem; }
.app-title { font-family:'Fraunces',serif; font-size:2.2rem; font-weight:900; line-height:1.1; margin:0; }
.app-title em { font-style:italic; font-weight:300; color:#d4a84b; }
.app-subtitle { color:#8c8a84; font-size:.9rem; margin-top:.5rem; }
.app-header { border-bottom:1px solid rgba(212,168,75,.2); padding-bottom:1.5rem; margin-bottom:2rem; }

.groq-badge { display:inline-flex; align-items:center; gap:.4rem; font-family:'DM Mono',monospace; font-size:.6rem; color:#4dd488; border:1px solid rgba(77,212,136,.25); padding:.2rem .6rem; margin-left:.75rem; }

.stTextInput > label, .stTextArea > label { font-family:'DM Mono',monospace !important; font-size:.7rem !important; letter-spacing:.12em !important; text-transform:uppercase !important; color:#d4a84b !important; }
.stTextInput input, .stTextArea textarea { background:#14141c !important; border:1px solid rgba(212,168,75,.25) !important; border-radius:3px !important; color:#e4e2dc !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color:#d4a84b !important; box-shadow:0 0 0 2px rgba(212,168,75,.1) !important; }

.stButton > button { background:#d4a84b !important; color:#0c0c10 !important; border:none !important; border-radius:3px !important; font-family:'DM Mono',monospace !important; font-size:.75rem !important; font-weight:700 !important; letter-spacing:.1em !important; text-transform:uppercase !important; padding:.65rem 2rem !important; transition:all .2s !important; }
.stButton > button:hover { background:#e8c97a !important; transform:translateY(-1px); box-shadow:0 4px 20px rgba(212,168,75,.3) !important; }

.stat-box { background:#14141c; border:1px solid rgba(212,168,75,.15); padding:1.25rem; text-align:center; }
.stat-value { font-family:'Fraunces',serif; font-size:1.8rem; font-weight:700; color:#d4a84b; line-height:1; }
.stat-label { font-family:'DM Mono',monospace; font-size:.6rem; color:#8c8a84; letter-spacing:.1em; text-transform:uppercase; margin-top:.3rem; }

.result-box { background:#14141c; border:1px solid rgba(212,168,75,.15); padding:1.5rem; margin-top:1.5rem; position:relative; }
.result-box::before { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background:linear-gradient(180deg,#d4a84b,transparent); }
.result-label { font-family:'DM Mono',monospace; font-size:.62rem; letter-spacing:.12em; text-transform:uppercase; color:#7a5e28; margin-bottom:.75rem; }

.chip { display:inline-block; font-family:'DM Mono',monospace; font-size:.62rem; padding:.3rem .75rem; border:1px solid rgba(212,168,75,.2); color:#7a5e28; margin:.25rem; }

.custom-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent); margin:1.5rem 0; }
.app-footer { font-family:'DM Mono',monospace; font-size:.62rem; color:#44433f; text-align:center; padding-top:2rem; }

[data-testid="stSidebar"] { background:#10101a !important; border-right:1px solid rgba(212,168,75,.12) !important; }
.stFileUploader { border:1px dashed rgba(212,168,75,.25) !important; border-radius:3px !important; background:#14141c !important; }
.stFileUploader label { color:#d4a84b !important; font-family:'DM Mono',monospace !important; font-size:.7rem !important; }
.streamlit-expanderHeader { font-family:'DM Mono',monospace !important; color:#d4a84b !important; background:#14141c !important; border:1px solid rgba(212,168,75,.2) !important; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_groq() -> Groq:
    """Crea el cliente de Groq si la API key esta disponible."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y anade tu clave antes de generar analisis."
        )
    return Groq(api_key=api_key)


@st.cache_data
def cargar_datos(archivo, separador: str) -> pd.DataFrame:
    """Carga el archivo tabular subido por el usuario."""
    nombre = archivo.name.lower()
    if nombre.endswith(".csv"):
        return pd.read_csv(archivo, sep=separador)
    return pd.read_excel(archivo)


def limpiar_codigo_llm(codigo: str) -> str:
    """Extrae el bloque util si el modelo devuelve fences Markdown."""
    codigo = (codigo or "").strip()
    if not codigo:
        raise ValueError("El modelo no devolvio codigo utilizable.")

    if "```" in codigo:
        for parte in codigo.split("```"):
            parte = parte.strip()
            if not parte:
                continue
            if parte.startswith("python"):
                parte = parte[len("python"):].strip()
            if "resultado" in parte or "figura" in parte or "df" in parte:
                return parte.strip()

    return codigo


def validar_codigo_generado(codigo: str) -> str:
    """Aplica validaciones basicas antes de ejecutar el codigo generado."""
    codigo_limpio = limpiar_codigo_llm(codigo)
    codigo_lower = codigo_limpio.lower()

    if len(codigo_limpio) > MAX_CODE_CHARS:
        raise ValueError("Codigo bloqueado: respuesta demasiado larga para ejecucion segura.")
    if codigo_limpio.count("\n") + 1 > MAX_CODE_LINES:
        raise ValueError("Codigo bloqueado: demasiadas lineas para ejecucion segura.")

    for patron, mensaje in PATRONES_BLOQUEADOS.items():
        if patron in codigo_lower:
            raise ValueError(f"Codigo bloqueado: {mensaje}")

    try:
        arbol = ast.parse(codigo_limpio)
    except SyntaxError as exc:
        raise ValueError("El modelo devolvio codigo Python no valido.") from exc

    nodos = list(ast.walk(arbol))
    if len(nodos) > MAX_AST_NODES:
        raise ValueError("Codigo bloqueado: complejidad sintactica excesiva.")

    for nodo in nodos:
        if isinstance(nodo, (ast.Import, ast.ImportFrom)):
            raise ValueError("Codigo bloqueado: no se permiten importaciones.")
        if isinstance(nodo, NODOS_BLOQUEADOS):
            raise ValueError(
                f"Codigo bloqueado: no se permite '{nodo.__class__.__name__}'."
            )
        if isinstance(nodo, ast.Name) and nodo.id in NOMBRES_BLOQUEADOS:
            raise ValueError(f"Codigo bloqueado: uso no permitido de '{nodo.id}'.")
        if isinstance(nodo, ast.Attribute) and nodo.attr in ATRIBUTOS_BLOQUEADOS:
            raise ValueError(f"Codigo bloqueado: atributo no permitido '{nodo.attr}'.")
        if isinstance(nodo, ast.Call):
            if isinstance(nodo.func, ast.Name) and nodo.func.id in NOMBRES_BLOQUEADOS:
                raise ValueError(f"Codigo bloqueado: llamada no permitida a '{nodo.func.id}'.")
            if isinstance(nodo.func, ast.Attribute) and isinstance(nodo.func.value, ast.Name):
                if nodo.func.value.id in NOMBRES_BLOQUEADOS:
                    raise ValueError(
                        f"Codigo bloqueado: acceso no permitido a '{nodo.func.value.id}'."
                    )

    if "resultado" not in codigo_limpio and "figura" not in codigo_limpio:
        raise ValueError(
            "El analisis no devolvio ninguna salida reconocible. Prueba a reformular la pregunta."
        )

    return codigo_limpio


def generar_codigo(groq: Groq, pregunta: str, tipos: dict, muestra: str) -> str:
    """Pide a Groq codigo Python para responder la pregunta sobre el DataFrame."""
    prompt = f"""Eres un analista de datos experto en Python y pandas.
Tienes un DataFrame llamado 'df' con estas columnas y tipos:
{json.dumps(tipos, indent=2, ensure_ascii=False)}

Muestra de los primeros datos:
{muestra}

El usuario pregunta: "{pregunta}"

Genera codigo Python valido que:
1. Analiza df para responder la pregunta.
2. Guarda el resultado en una variable llamada 'resultado'.
3. Si el resultado es un numero, texto o lista: resultado = el valor directamente.
4. Si el resultado es un grafico: usa plotly express (px) y guarda la figura en 'figura'.
5. Si el resultado es una tabla: resultado = df_resultado (un DataFrame).

REGLAS CRITICAS:
- Usa solo: pandas (pd), plotly.express (px), plotly.graph_objects (go).
- No uses importaciones, print, display, matplotlib ni seaborn.
- No uses bloques try/except.
- El codigo debe ser ejecutable directamente.
- Si calculas fechas usa pd.to_datetime().
- Para graficos aplica template='plotly_dark'.

Responde solo con codigo Python. Sin explicaciones. Sin markdown. Sin comentarios."""

    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=800,
    )
    contenido = response.choices[0].message.content or ""  # type: ignore[union-attr]
    return validar_codigo_generado(contenido)


def ejecutar_codigo(codigo: str, df: pd.DataFrame):
    """Ejecuta el codigo validado en un entorno restringido."""
    entorno = {
        "__builtins__": ALLOWED_BUILTINS,
        "df": df.copy(),
        "pd": pd,
        "px": px,
        "go": go,
        "resultado": None,
        "figura": None,
    }
    exec(codigo, entorno, entorno)
    resultado = entorno.get("resultado")
    figura = entorno.get("figura")

    if figura is not None and not isinstance(figure := figura, go.Figure):
        raise ValueError("La variable 'figura' debe ser un objeto Plotly valido.")

    tipos_permitidos = (pd.DataFrame, pd.Series, str, int, float, bool, list, dict, tuple, type(None))
    if not isinstance(resultado, tipos_permitidos):
        raise ValueError("La variable 'resultado' tiene un tipo no permitido.")

    if isinstance(resultado, pd.DataFrame) and resultado.shape[0] > 20000:
        raise ValueError("La salida tabular es demasiado grande para mostrarse de forma segura.")

    return resultado, figure if figura is not None else None


with st.sidebar:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem\">// Cargar datos</div>",
        unsafe_allow_html=True,
    )

    archivo = st.file_uploader(
        "Sube tu CSV o Excel",
        type=["csv", "xlsx", "xls"],
        help="El archivo se procesa en la app y no se usa para busqueda web ni para servicios externos adicionales.",
    )

    separador = st.selectbox("Separador CSV", [",", ";", "|", "\\t"], index=0)

    st.markdown(
        """
    <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;
        line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
        <span style="color:#4dd488">OK</span> Modelo: Llama 3.3 70B<br>
        <span style="color:#4dd488">OK</span> Proveedor: Groq<br>
        <span style="color:#4dd488">OK</span> Salida: tablas, valores y graficos Plotly<br>
        <span style="color:#d4a84b">AVISO</span> Nota: revisa los resultados antes de usarlos
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:.58rem;color:#44433f;margin-top:1.5rem">
        P10  Dashboard con lenguaje natural<br>
        <a href="https://github.com/chema74/portfolio-ia-aplicada/tree/main/portfolio/p10-dashboard-lenguaje-natural" style="color:#7a5e28">Ver proyecto en GitHub</a>
    </div>""",
        unsafe_allow_html=True,
    )


st.markdown(
    """
<div class="app-header">
  <div class="app-tag">P10  Dashboard con lenguaje natural  Portfolio IA Aplicada
    <span class="groq-badge">Groq  Llama 3.3 70B</span>
  </div>
  <div class="app-title">Explora tus datos con <em>lenguaje natural</em></div>
  <div class="app-subtitle">
    La version actual permite cargar un CSV o Excel y generar analisis y visualizaciones bajo demanda a partir de preguntas en espanol.
  </div>
</div>""",
    unsafe_allow_html=True,
)

st.info(
    "Usa datos no sensibles cuando sea posible. El analisis depende de codigo generado por un LLM y conviene revisar el resultado antes de tomar decisiones."
)

if archivo is None:
    st.markdown(
        """
    <div style="border:1px dashed rgba(212,168,75,.2);padding:3rem 2rem;text-align:center;margin-top:1rem">
      <div style="font-size:2.5rem;margin-bottom:1rem"></div>
      <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#8c8a84;margin-bottom:.75rem">
        Sube un CSV o Excel para empezar
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:.63rem;color:#44433f;letter-spacing:.06em;line-height:1.9">
        Despues podras preguntar sobre tus datos en espanol.<br>
        Ejemplos: "Cual fue el mes con mas ventas?"  "Muestrame un grafico por categoria"<br>
        <span style="color:#4dd488">? Anlisis con Groq y ejecucion local con validaciones basicas</span>
      </div>
    </div>""",
        unsafe_allow_html=True,
    )
    st.stop()

try:
    df = cargar_datos(archivo, separador)
except Exception as exc:
    st.error(
        "No se pudo leer el archivo. Revisa el formato, la hoja seleccionada o el separador si es un CSV."
    )
    with st.expander("Ver detalle tecnico"):
        st.code(str(exc))
    st.stop()

st.markdown(
    f"""
<div style="display:flex;justify-content:space-between;align-items:baseline;
    border-bottom:1px solid rgba(212,168,75,.2);padding-bottom:1rem;margin-bottom:1.5rem">
  <div>
    <span style="font-family:'Fraunces',serif;font-size:1.3rem;font-weight:700">
      {archivo.name}
    </span>
    <span style="font-family:'DM Mono',monospace;font-size:.62rem;color:#7a5e28;margin-left:1rem">
      DATASET CARGADO
    </span>
  </div>
</div>""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
stats = [
    (f"{len(df):,}", "filas"),
    (str(len(df.columns)), "columnas"),
    (str(df.select_dtypes(include="number").shape[1]), "columnas numericas"),
    (f"{df.isnull().sum().sum():,}", "valores vacos"),
]
for col, (valor, etiqueta) in zip([c1, c2, c3, c4], stats):
    with col:
        st.markdown(
            f"""
        <div class="stat-box">
          <div class="stat-value">{valor}</div>
          <div class="stat-label">{etiqueta}</div>
        </div>""",
            unsafe_allow_html=True,
        )

with st.expander("Vista previa de los datos"):
    st.dataframe(df.head(20), use_container_width=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

cols_num = df.select_dtypes(include="number").columns.tolist()
cols_cat = df.select_dtypes(include=["object", "category"]).columns.tolist()

sugerencias = [
    "Cuantas filas tiene el dataset?",
    "Cuales son los valores unicos de cada columna?",
    "Muestrame un resumen estadistico",
]
if cols_num:
    sugerencias.append(f"Cual es el maximo de {cols_num[0]}?")
    sugerencias.append(f"Muestrame un histograma de {cols_num[0]}")
if cols_cat:
    sugerencias.append(f"Cuantos registros hay por {cols_cat[0]}?")
    sugerencias.append(f"Muestrame un grafico de barras por {cols_cat[0]}")
if len(cols_num) >= 2:
    sugerencias.append(f"Existe correlacion entre {cols_num[0]} y {cols_num[1]}?")

st.markdown(
    "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;margin-bottom:.75rem\">Preguntas sugeridas</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "".join(f'<span class="chip">{s}</span>' for s in sugerencias[:6]),
    unsafe_allow_html=True,
)
st.caption("Son ejemplos de consulta. Puedes escribir la pregunta en el cuadro inferior.")

st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

col_q, col_btn = st.columns([5, 1])
with col_q:
    pregunta = st.text_input(
        "Escribe tu pregunta",
        placeholder="Ej: Cual fue el mes con mas ventas?  Muestrame un grafico de barras por categoria",
    )
with col_btn:
    st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
    preguntar = st.button("Analizar", use_container_width=True)

if preguntar and pregunta.strip():
    tipos = {col: str(dtype) for col, dtype in df.dtypes.items()}
    muestra = df.head(3).to_string(index=False)

    try:
        groq_client = get_groq()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    with st.spinner("Analizando con Groq..."):
        try:
            codigo = generar_codigo(groq_client, pregunta.strip(), tipos, muestra)
        except Exception as exc:
            st.error(
                "No se pudo generar un analisis valido para esta pregunta. Prueba a formularla de forma mas concreta."
            )
            with st.expander("Ver detalle tecnico"):
                st.code(str(exc))
            st.stop()

    try:
        resultado, figura = ejecutar_codigo(codigo, df)
    except Exception as exc:
        st.error(
            "Se gener codigo, pero no pudo ejecutarse correctamente con este dataset o esta pregunta."
        )
        with st.expander("Ver codigo generado"):
            st.code(codigo, language="python")
        with st.expander("Ver detalle tecnico"):
            st.code(str(exc))
        st.stop()

    st.markdown(
        f"""
    <div style="background:#14141c;border:1px solid rgba(212,168,75,.2);
        padding:1rem 1.5rem;margin:1.5rem 0 1rem">
      <span style="font-family:'DM Mono',monospace;font-size:.62rem;
          letter-spacing:.12em;text-transform:uppercase;color:#7a5e28">
          Respuesta a:
      </span>
      <span style="font-family:'Fraunces',serif;font-size:1rem;
          font-style:italic;color:#c8c6c0;margin-left:.75rem">
          \"{pregunta}\"
      </span>
    </div>""",
        unsafe_allow_html=True,
    )

    if figura is not None:
        figura.update_layout(
            paper_bgcolor="#14141c",
            plot_bgcolor="#14141c",
            font_color="#e4e2dc",
            font_family="DM Sans",
        )
        st.plotly_chart(figura, use_container_width=True)
    elif isinstance(resultado, pd.DataFrame):
        st.dataframe(resultado, use_container_width=True)
    elif resultado is not None:
        st.markdown(
            f"""
        <div class="result-box">
          <div class="result-label">Resultado</div>
          <div style="font-family:'Fraunces',serif;font-size:1.5rem;
              font-weight:700;color:#d4a84b">{resultado}</div>
        </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.info("El analisis termino, pero no devolvio un resultado visible. Prueba a reformular la pregunta.")

    with st.expander("Ver codigo generado por Groq"):
        st.code(codigo, language="python")

elif preguntar and not pregunta.strip():
    st.warning("Escribe una pregunta sobre tus datos antes de analizar.")

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='app-footer'>P10  Dashboard con lenguaje natural  Groq + Llama 3.3 70B  Portfolio IA Aplicada  Jose Maria  Sevilla</div>",
    unsafe_allow_html=True,
)

