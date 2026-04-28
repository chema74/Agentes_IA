"""
P04  Agente de criba de candidatos
==================================
Autor: Jos Mara
Stack: Groq  ChromaDB  sentence-transformers  PyMuPDF  Streamlit

Cmo funciona:
1. El usuario define el puesto y las competencias requeridas.
2. Sube uno o varios CVs en PDF.
3. La app extrae texto e indexa localmente los documentos.
4. Groq genera una preevaluacion documental estructurada por candidato.
5. La salida sirve como apoyo a la criba inicial y requiere revision humana.
"""

import json
import os
import shutil
import time

import chromadb
import fitz
import streamlit as st
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

CHROMA_PATH = "./chroma_db_p04"
COLLECTION = "candidatos"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

CLAVES_OBLIGATORIAS = {
    "nombre",
    "puntuacion",
    "nivel_recomendacion",
    "fortalezas",
    "debilidades",
    "cumple_experiencia",
    "competencias_detectadas",
    "preguntas_entrevista",
    "resumen",
}

st.set_page_config(
    page_title="Agente de criba de candidatos",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,300&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:#0c0c10;color:#e4e2dc}
.stApp{background:#0c0c10}#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:2rem;padding-bottom:2rem;max-width:1100px}
.app-tag{font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;color:#d4a84b;margin-bottom:.75rem}
.app-title{font-family:'Fraunces',serif;font-size:2.2rem;font-weight:900;line-height:1.1;margin:0}
.app-title em{font-style:italic;font-weight:300;color:#d4a84b}
.app-subtitle{color:#8c8a84;font-size:.9rem;margin-top:.5rem}
.app-header{border-bottom:1px solid rgba(212,168,75,.2);padding-bottom:1.5rem;margin-bottom:2rem}
.groq-badge{display:inline-flex;align-items:center;gap:.4rem;font-family:'DM Mono',monospace;font-size:.6rem;color:#4dd488;border:1px solid rgba(77,212,136,.25);padding:.2rem .6rem;margin-left:.75rem}
.stTextInput>label,.stTextArea>label,.stSelectbox>label{font-family:'DM Mono',monospace !important;font-size:.7rem !important;letter-spacing:.12em !important;text-transform:uppercase !important;color:#d4a84b !important}
.stTextInput input,.stTextArea textarea{background:#14141c !important;border:1px solid rgba(212,168,75,.25) !important;border-radius:3px !important;color:#e4e2dc !important}
[data-baseweb="select"]>div{background:#14141c !important;border:1px solid rgba(212,168,75,.25) !important;border-radius:3px !important;color:#e4e2dc !important}
.stButton>button{background:#d4a84b !important;color:#0c0c10 !important;border:none !important;border-radius:3px !important;font-family:'DM Mono',monospace !important;font-size:.75rem !important;font-weight:700 !important;letter-spacing:.1em !important;text-transform:uppercase !important;padding:.65rem 2rem !important}
.stButton>button:hover{background:#e8c97a !important;transform:translateY(-1px)}
.candidato-card{background:#14141c;border:1px solid rgba(212,168,75,.15);padding:1.75rem;margin-bottom:.75rem;position:relative}
.candidato-card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(180deg,#d4a84b,transparent)}
.candidato-rank{position:absolute;top:1.25rem;right:1.5rem;font-family:'Fraunces',serif;font-size:2.2rem;font-weight:900;color:rgba(212,168,75,.15);line-height:1}
.candidato-nombre{font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;margin-bottom:.3rem}
.score-num{font-family:'Fraunces',serif;font-size:1.8rem;font-weight:900;line-height:1}
.comp-item{padding:.3rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.85rem}
.aviso-box{background:rgba(232,120,120,.05);border:1px solid rgba(232,120,120,.25);padding:1rem 1.25rem;margin-bottom:1rem;font-size:.875rem;color:#e8b8b8}
.custom-divider{height:1px;background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent);margin:1.5rem 0}
.app-footer{font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;text-align:center;padding-top:2rem}
.chip{display:inline-block;font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.15);color:#8c8a84;margin:.2rem}
[data-testid="stSidebar"]{background:#10101a !important;border-right:1px solid rgba(212,168,75,.12) !important}
</style>""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_groq() -> Groq:
    """Crea el cliente de Groq si la API key est disponible."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y anade tu clave antes de evaluar candidatos."
        )
    return Groq(api_key=api_key)


@st.cache_resource
def get_chroma():
    """Inicializa la coleccin persistente para CVs."""
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def extraer_texto_cv(bytes_pdf, nombre):
    """Extrae texto del CV y genera fragmentos indexables."""
    try:
        doc = fitz.open(stream=bytes_pdf, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"No se pudo abrir el PDF '{nombre}'.") from exc

    texto_completo = ""
    try:
        for pagina in doc:
            texto_completo += pagina.get_text("text") + "\n"
    finally:
        doc.close()

    texto_completo = texto_completo.strip()
    if len(texto_completo) < 80:
        raise ValueError(
            f"No se pudo extraer suficiente texto de '{nombre}'. Comprueba que el CV no sea una imagen escaneada sin texto seleccionable."
        )

    chunks = []
    inicio = 0
    while inicio < len(texto_completo):
        chunk = texto_completo[inicio:inicio + CHUNK_SIZE].strip()
        if len(chunk) > 50:
            chunks.append(
                {
                    "texto": chunk,
                    "fuente": nombre,
                    "pagina": 1,
                    "id": f"{nombre}_c{inicio}",
                }
            )
        inicio += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks, texto_completo[:3000]


def indexar(collection, chunks, nombre):
    """Elimina versiones previas e indexa el CV."""
    try:
        ids = collection.get(where={"fuente": nombre})["ids"]
        if ids:
            collection.delete(ids=ids)
    except Exception:
        pass

    if chunks:
        collection.upsert(
            documents=[c["texto"] for c in chunks],
            ids=[c["id"] for c in chunks],
            metadatas=[{"fuente": c["fuente"], "pagina": c["pagina"]} for c in chunks],
        )


def extraer_json_objeto(texto: str) -> dict:
    """Extrae y valida el primer objeto JSON til de la respuesta del modelo."""
    if not texto:
        raise ValueError("El modelo no devolvi contenido.")

    texto = texto.strip()
    candidatos = []

    if "```" in texto:
        for bloque in texto.split("```"):
            bloque = bloque.strip()
            if not bloque:
                continue
            if bloque.startswith("json"):
                bloque = bloque[4:].strip()
            candidatos.append(bloque)

    candidatos.append(texto)

    for candidato in candidatos:
        inicio = candidato.find("{")
        while inicio != -1:
            profundidad = 0
            for indice in range(inicio, len(candidato)):
                caracter = candidato[indice]
                if caracter == "{":
                    profundidad += 1
                elif caracter == "}":
                    profundidad -= 1
                    if profundidad == 0:
                        fragmento = candidato[inicio:indice + 1]
                        try:
                            data = json.loads(fragmento)
                            if isinstance(data, dict):
                                return data
                        except json.JSONDecodeError:
                            pass
                        break
            inicio = candidato.find("{", inicio + 1)

    raise ValueError("La respuesta del modelo no contenia un JSON valido.")


def normalizar_evaluacion(data: dict, nombre_archivo: str) -> dict:
    """Valida la estructura minima esperada para la evaluacion."""
    faltantes = CLAVES_OBLIGATORIAS - set(data.keys())
    if faltantes:
        raise ValueError(f"Faltan claves obligatorias en la evaluacion: {', '.join(sorted(faltantes))}.")

    try:
        puntuacion = float(data.get("puntuacion", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("La puntuacion devuelta por el modelo no es valida.") from exc

    evaluacion = {
        "nombre": str(data.get("nombre") or nombre_archivo).strip() or nombre_archivo,
        "puntuacion": max(0.0, min(10.0, round(puntuacion, 1))),
        "nivel_recomendacion": str(data.get("nivel_recomendacion", "Seal orientativa")).strip(),
        "fortalezas": [str(x).strip() for x in data.get("fortalezas", []) if str(x).strip()],
        "debilidades": [str(x).strip() for x in data.get("debilidades", []) if str(x).strip()],
        "cumple_experiencia": bool(data.get("cumple_experiencia", False)),
        "competencias_detectadas": [
            str(x).strip() for x in data.get("competencias_detectadas", []) if str(x).strip()
        ],
        "preguntas_entrevista": [
            str(x).strip() for x in data.get("preguntas_entrevista", []) if str(x).strip()
        ],
        "resumen": str(data.get("resumen", "")).strip(),
        "archivo": nombre_archivo,
    }

    if not evaluacion["fortalezas"]:
        raise ValueError("La evaluacion no incluyo fortalezas utilizables.")
    if not evaluacion["preguntas_entrevista"]:
        raise ValueError("La evaluacion no incluyo preguntas de entrevista utilizables.")

    return evaluacion


def evaluar_candidato(groq_client, nombre_cv, texto_cv, descripcion_puesto, competencias, experiencia_min):
    """Solicita al modelo una preevaluacion documental del CV."""
    prompt = f"""Evalua este CV como apoyo a una criba inicial documental. No tomes decisiones de contratacion.

PUESTO: {descripcion_puesto}
COMPETENCIAS REQUERIDAS: {competencias}
EXPERIENCIA MNIMA: {experiencia_min}

CV DE {nombre_cv}:
{texto_cv}

Genera un JSON con:
nombre: nombre del candidato extrado del CV (o el nombre del archivo si no aparece)
puntuacion: numero del 1 al 10 como senal orientativa interna
nivel_recomendacion: "Ajuste alto", "Ajuste medio", "Ajuste parcial" o "Ajuste debil"
fortalezas: lista de 3 puntos fuertes observables en el CV para este puesto
debilidades: lista de 2-3 gaps o puntos debiles respecto al perfil
cumple_experiencia: true o false
competencias_detectadas: lista de competencias requeridas detectables en el CV
preguntas_entrevista: lista de 3 preguntas especificas para validar el perfil
resumen: 2-3 frases de valoracion global

IMPORTANTE:
- Evalua nicamente lo que aparece en el CV.
- No afirmes objetividad total ni ausencia de sesgo.
- No emitas un dictamen definitivo de contratacion.
- Devuelve solo JSON valido, sin markdown.
"""

    respuesta = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=800,
    )
    contenido = respuesta.choices[0].message.content or ""
    data = extraer_json_objeto(contenido)
    return normalizar_evaluacion(data, nombre_cv)


if "candidatos_evaluados" not in st.session_state:
    st.session_state.candidatos_evaluados = []
if "cvs_indexados" not in st.session_state:
    st.session_state.cvs_indexados = {}

with st.sidebar:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem\">// Descripcin del puesto</div>",
        unsafe_allow_html=True,
    )
    descripcion = st.text_area(
        "Descripcin del puesto",
        placeholder="Ej: Buscamos un responsable de ventas con experiencia en B2B...",
        height=100,
    )
    competencias = st.text_area(
        "Competencias requeridas",
        placeholder="Ej: Negociacin, CRM, ingls B2, gestin de equipos...",
        height=70,
    )
    experiencia_min = st.selectbox(
        "Experiencia minima",
        ["Sin requisito", "1 ao", "2 aos", "3 aos", "5 aos", "10 aos"],
    )

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    archivos = st.file_uploader("Sube los CVs en PDF", type=["pdf"], accept_multiple_files=True)

    if st.button("Borrar todo", use_container_width=True):
        st.cache_resource.clear()
        time.sleep(0.3)
        shutil.rmtree(CHROMA_PATH, ignore_errors=True)
        st.session_state.candidatos_evaluados = []
        st.session_state.cvs_indexados = {}
        st.rerun()

    st.markdown(
        """
<div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
<span style="color:#e87878"></span> Revisin humana obligatoria<br>
<span style="color:#4dd488"></span> Solo herramienta de apoyo documental<br>
<span style="color:#d4a84b"></span> No sustituye decisiones de RR. HH.
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="app-header">
  <div class="app-tag">P04  Agente de criba de candidatos  Portfolio IA Aplicada
    <span class="groq-badge"> Groq  ChromaDB local</span></div>
  <div class="app-title">Criba inicial de <em>candidatos</em></div>
  <div class="app-subtitle">Sube CVs, obtn senales orientativas de ajuste al perfil y prepara mejor la revision humana y la entrevista.</div>
</div>""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="aviso-box">
 <strong>Aviso importante:</strong> esta herramienta apoya una preevaluacion documental inicial. No toma decisiones de contratacion, no garantiza objetividad total y no elimina sesgos por si misma. Cualquier resultado debe revisarse antes de usarlo en procesos reales de seleccion.
</div>""",
    unsafe_allow_html=True,
)

if not descripcion.strip():
    st.info("Define la descripcin del puesto en el panel izquierdo para comenzar.")
    st.stop()

if archivos and st.button("Evaluar candidatos ", use_container_width=False):
    try:
        groq_client = get_groq()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    try:
        coleccion = get_chroma()
    except Exception as exc:
        st.error("No se pudo inicializar la base documental local de CVs.")
        with st.expander("Ver detalle tcunico"):
            st.code(str(exc))
        st.stop()

    for archivo in archivos:
        if archivo.name not in st.session_state.cvs_indexados:
            with st.spinner(f"Evaluando {archivo.name}..."):
                try:
                    chunks, texto_completo = extraer_texto_cv(archivo.read(), archivo.name)
                    indexar(coleccion, chunks, archivo.name)
                    evaluacion = evaluar_candidato(
                        groq_client,
                        archivo.name,
                        texto_completo,
                        descripcion,
                        competencias,
                        experiencia_min,
                    )
                    st.session_state.cvs_indexados[archivo.name] = evaluacion
                except ValueError as exc:
                    st.error(f"No se pudo evaluar {archivo.name}: {exc}")
                except Exception as exc:
                    st.error(f"Se produjo un error al procesar {archivo.name}.")
                    with st.expander(f"Ver detalle tcunico: {archivo.name}"):
                        st.code(str(exc))

    todos = list(st.session_state.cvs_indexados.values())
    todos.sort(key=lambda x: x.get("puntuacion", 0), reverse=True)
    st.session_state.candidatos_evaluados = todos
    st.rerun()

if st.session_state.candidatos_evaluados:
    candidatos = st.session_state.candidatos_evaluados
    st.markdown(
        f"""
    <div style="display:flex;justify-content:space-between;align-items:baseline;
        border-bottom:1px solid rgba(212,168,75,.2);padding-bottom:1rem;margin-bottom:1.5rem">
      <span style="font-family:'Fraunces',serif;font-size:1.3rem;font-weight:700">
        Ranking orientativo de {len(candidatos)} candidato{'s' if len(candidatos)!=1 else ''}
      </span>
      <span style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f">
        Seal interna para revision humana
      </span>
    </div>""",
        unsafe_allow_html=True,
    )

    for indice, candidato in enumerate(candidatos, 1):
        score = candidato.get("puntuacion", 0)
        nivel = candidato.get("nivel_recomendacion", "")
        color_nivel = {
            "Ajuste alto": "#4dd488",
            "Ajuste medio": "#d4a84b",
            "Ajuste parcial": "#d4a84b",
            "Ajuste debil": "#e87878",
        }.get(nivel, "#d4a84b")
        cumple_exp = candidato.get("cumple_experiencia", False)

        st.markdown(
            f"""
        <div class="candidato-card">
        <div class="candidato-rank">#{indice}</div>
        <div style="display:flex;align-items:center;gap:1.5rem;margin-bottom:1rem;flex-wrap:wrap">
          <div class="candidato-nombre">{candidato.get('nombre', candidato.get('archivo',''))}</div>
          <div class="score-num" style="color:{color_nivel}">{score}/10</div>
          <div style="font-family:'DM Mono',monospace;font-size:.65rem;padding:.2rem .6rem;background:rgba(212,168,75,.06);color:{color_nivel};border:1px solid {color_nivel}40">{nivel}</div>
          <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:{'#4dd488' if cumple_exp else '#e87878'}">
            {' Cumple experiencia declarada' if cumple_exp else ' No acredita experiencia minima declarada'}
          </div>
        </div>
        <div style="font-size:.875rem;color:#c8c6c0;line-height:1.8;margin-bottom:.75rem">{candidato.get('resumen','')}</div>
        </div>""",
            unsafe_allow_html=True,
        )

        col_f, col_d, col_q = st.columns(3)
        with col_f:
            st.markdown(
                "<div style=\"font-family:'DM Mono',monospace;font-size:.6rem;color:#4dd488;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem\">Fortalezas detectadas</div>",
                unsafe_allow_html=True,
            )
            for fortaleza in candidato.get("fortalezas", []):
                st.markdown(
                    f'<div class="comp-item" style="color:#a8e8c0"> {fortaleza}</div>',
                    unsafe_allow_html=True,
                )
        with col_d:
            st.markdown(
                "<div style=\"font-family:'DM Mono',monospace;font-size:.6rem;color:#e87878;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem\">Gaps o dudas</div>",
                unsafe_allow_html=True,
            )
            for debilidad in candidato.get("debilidades", []):
                st.markdown(
                    f'<div class="comp-item" style="color:#e8b8b8"> {debilidad}</div>',
                    unsafe_allow_html=True,
                )
        with col_q:
            st.markdown(
                "<div style=\"font-family:'DM Mono',monospace;font-size:.6rem;color:#68a8e8;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem\">Preguntas de entrevista</div>",
                unsafe_allow_html=True,
            )
            for pregunta_entrevista in candidato.get("preguntas_entrevista", []):
                st.markdown(
                    f'<div class="comp-item" style="color:#a0c0e8"> {pregunta_entrevista}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

elif archivos:
    st.info("Pulsa 'Evaluar candidatos' para generara la criba inicial de los CVs subidos.")
else:
    st.markdown(
        """
    <div style="border:1px dashed rgba(212,168,75,.2);padding:3rem;text-align:center;margin-top:1rem">
    <div style="font-size:2.5rem;margin-bottom:1rem"></div>
    <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:#8c8a84;margin-bottom:.5rem">
      Define el puesto y sube los CVs en PDF
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;line-height:1.9">
      La app generara una preevaluacion documental orientativa con fortalezas,<br>
      gaps y preguntas de entrevista para revision humana.
    </div>
    </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="app-footer">P04  Agente de criba de candidatos  Groq + ChromaDB  Portfolio IA Aplicada  Jos Mara  Sevilla</div>',
    unsafe_allow_html=True,
)
