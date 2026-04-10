"""
P03 - Agente de Evaluacion y Preparacion de Licitaciones
========================================================
Autor : Jose Maria
Stack : Groq - ChromaDB - sentence-transformers - PyMuPDF - Streamlit
Coste : GRATUITO
"""

import json
import os
import shutil

import chromadb
import fitz
import streamlit as st
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

CHROMA_PATH = "./chroma_db_p03"
COLLECTION = "licitaciones"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K = 6
MAX_TEXTO_ANALISIS = 5000

st.set_page_config(
    page_title="Evaluador de Licitaciones IA",
    page_icon=":clipboard:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,300&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
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
.result-block{background:#14141c;border:1px solid rgba(212,168,75,.15);padding:1.5rem;margin-bottom:1rem;position:relative}
.result-block::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(180deg,#d4a84b,transparent)}
.result-label{font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;margin-bottom:.6rem}
.riesgo-item{padding:.45rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem;color:#e8b8b8}
.req-item{padding:.45rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem}
.msg-user{background:rgba(212,168,75,.06);border:1px solid rgba(212,168,75,.12);padding:.9rem 1.1rem;margin-bottom:.4rem;font-size:.875rem}
.msg-bot{background:#14141c;border:1px solid rgba(212,168,75,.1);border-left:3px solid #d4a84b;padding:1.1rem 1.4rem;margin-bottom:.75rem;font-size:.875rem;line-height:1.85;color:#e4e2dc}
.msg-role{font-family:'DM Mono',monospace;font-size:.58rem;color:#44433f;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.35rem}
.custom-divider{height:1px;background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent);margin:1.5rem 0}
.app-footer{font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;text-align:center;padding-top:2rem}
[data-testid="stSidebar"]{background:#10101a !important;border-right:1px solid rgba(212,168,75,.12) !important}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_groq():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Falta GROQ_API_KEY. Configura tu clave en el archivo .env.")
    return Groq(api_key=api_key)


@st.cache_resource
def get_chroma():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION, embedding_function=ef, metadata={"hnsw:space": "cosine"}
    )


def extraer_todo(bytes_pdf: bytes, nombre: str):
    """Lee el PDF una sola vez y devuelve texto completo y chunks."""
    doc = fitz.open(stream=bytes_pdf, filetype="pdf")
    texto_completo = ""
    chunks = []
    for num_pag, pag in enumerate(doc, 1):
        texto = pag.get_text("text").strip()
        if not texto:
            continue
        texto_completo += texto + "\n"
        inicio = 0
        while inicio < len(texto):
            chunk = texto[inicio : inicio + CHUNK_SIZE].strip()
            if len(chunk) > 50:
                chunks.append(
                    {
                        "texto": chunk,
                        "fuente": nombre,
                        "pagina": num_pag,
                        "offset": inicio,
                        "id": f"{nombre}_p{num_pag}_c{inicio}",
                    }
                )
            inicio += CHUNK_SIZE - CHUNK_OVERLAP
    doc.close()
    return texto_completo, chunks


def indexar(collection, chunks, nombre):
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
            metadatas=[
                {"fuente": c["fuente"], "pagina": c["pagina"], "offset": c["offset"]}
                for c in chunks
            ],
        )


def recuperar_fuentes_indexadas(collection):
    """
    Recupera solo fuentes indexadas en Chroma.
    No reconstruye texto canonico desde chunks solapados.
    """
    if collection.count() == 0:
        return set()
    data = collection.get(include=["metadatas"])
    fuentes = set()
    for meta in data.get("metadatas", []):
        if meta and meta.get("fuente"):
            fuentes.add(meta["fuente"])
    return fuentes


def _extraer_objetos_json(texto: str):
    """Extrae objetos JSON balanceados sin depender de find/rfind."""
    objetos = []
    inicio = None
    profundidad = 0
    en_cadena = False
    escape = False
    for i, ch in enumerate(texto):
        if en_cadena:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "\"":
                en_cadena = False
            continue

        if ch == "\"":
            en_cadena = True
        elif ch == "{":
            if profundidad == 0:
                inicio = i
            profundidad += 1
        elif ch == "}" and profundidad > 0:
            profundidad -= 1
            if profundidad == 0 and inicio is not None:
                objetos.append(texto[inicio : i + 1])
                inicio = None
    return objetos


def parsear_json_llm(raw: str) -> dict:
    """Extrae JSON valido del modelo y valida una estructura minima."""
    if not raw or not raw.strip():
        raise ValueError("El modelo devolvio una respuesta vacia.")

    bruto = raw.strip()
    bloques = [bruto]
    if "```" in bruto:
        for parte in bruto.split("```"):
            parte = parte.strip()
            if parte.lower().startswith("json"):
                parte = parte[4:].strip()
            if parte:
                bloques.append(parte)

    claves_obligatorias = {
        "titulo_licitacion",
        "organismo_convocante",
        "presupuesto_base",
        "plazo_ejecucion",
        "fecha_presentacion",
        "puntuacion_viabilidad",
        "recomendacion",
        "requisitos_tecnicos",
        "requisitos_economicos",
        "criterios_puntuacion",
        "riesgos",
        "fortalezas_candidato",
        "resumen_ejecutivo",
        "proximos_pasos",
    }

    errores = []
    vistos = set()
    for bloque in bloques:
        objetos = sorted(_extraer_objetos_json(bloque), key=len, reverse=True)
        for candidato in objetos:
            if candidato in vistos:
                continue
            vistos.add(candidato)
            try:
                data = json.loads(candidato)
            except json.JSONDecodeError:
                continue

            if not isinstance(data, dict):
                continue

            faltantes = sorted(claves_obligatorias - set(data.keys()))
            if faltantes:
                errores.append("Faltan claves: " + ", ".join(faltantes))
                continue

            campos_lista = [
                "requisitos_tecnicos",
                "requisitos_economicos",
                "criterios_puntuacion",
                "riesgos",
                "fortalezas_candidato",
                "proximos_pasos",
            ]
            tipos_invalidos = [
                c for c in campos_lista if not isinstance(data.get(c), list)
            ]
            if tipos_invalidos:
                errores.append(
                    "Campos que deben ser lista: " + ", ".join(tipos_invalidos)
                )
                continue
            return data

    if errores:
        raise ValueError("Respuesta JSON invalida del modelo. " + errores[0])
    raise ValueError(
        "No se pudo extraer un JSON valido y completo desde la respuesta del modelo."
    )


def buscar(collection, pregunta: str, k: int = TOP_K):
    if collection.count() == 0:
        return []
    r = collection.query(
        query_texts=[pregunta],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    if r and r["documents"]:
        for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
            chunks.append(
                {
                    "texto": doc,
                    "fuente": meta.get("fuente", "-"),
                    "pagina": meta.get("pagina", "-"),
                    "score": round(1 - dist, 3),
                }
            )
    return chunks


def analizar_licitacion(
    groq_c, texto: str, empresa: str, sector: str, facturacion: str, experiencia: str
) -> dict:
    prompt = f"""Analiza este pliego de condiciones y evalua la viabilidad para esta empresa.

EMPRESA CANDIDATA:
Nombre: {empresa or "Empresa consultora"}
Sector: {sector or "Servicios profesionales"}
Facturacion anual: {facturacion}
Anos de experiencia: {experiencia}

PLIEGO (extracto maximo de {MAX_TEXTO_ANALISIS} caracteres):
{texto[:MAX_TEXTO_ANALISIS]}

Genera un JSON con:
titulo_licitacion: titulo o referencia del contrato
organismo_convocante: entidad que convoca
presupuesto_base: importe del contrato
plazo_ejecucion: duracion del contrato
fecha_presentacion: plazo de presentacion de ofertas
puntuacion_viabilidad: numero del 1 al 10
recomendacion: "Concursar" o "Considerar con cautela" o "No recomendado"
requisitos_tecnicos: lista de 3-5 requisitos tecnicos clave
requisitos_economicos: lista de 2-3 requisitos economicos
criterios_puntuacion: lista de objetos con criterio y peso_pct
riesgos: lista de 3 riesgos del pliego
fortalezas_candidato: lista de 2-3 puntos donde puede destacar
resumen_ejecutivo: 3-4 frases de valoracion global
proximos_pasos: lista de 3 acciones si se decide concursar

Solo JSON valido. Sin markdown."""

    r = groq_c.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1500,
    )
    raw = r.choices[0].message.content.strip()
    return parsear_json_llm(raw)


def responder_consulta(groq_c, pregunta: str, contexto: list, historial: list) -> str:
    """Responde preguntas libres sobre el pliego."""
    ctx_str = "\n\n---\n\n".join([f"[Pag. {c['pagina']}]\n{c['texto']}" for c in contexto])
    system = (
        "Eres un experto en contratacion publica y licitaciones. "
        "Responde exclusivamente basandote en el pliego cargado. "
        "Cita siempre la pagina de referencia. "
        "Si no encuentras la informacion, dilo claramente. "
        "Responde en espanol."
    )
    msgs = [{"role": "system", "content": system}]
    for m in historial[-4:]:
        msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": f"PLIEGO:\n{ctx_str}\n\nPREGUNTA: {pregunta}"})
    r = groq_c.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=msgs,
        temperature=0.1,
        max_tokens=700,
    )
    return r.choices[0].message.content


if "analisis_p03" not in st.session_state:
    st.session_state.analisis_p03 = None
if "chat_p03" not in st.session_state:
    st.session_state.chat_p03 = []
if "docs_p03" not in st.session_state:
    st.session_state.docs_p03 = set()
if "texto_p03" not in st.session_state:
    st.session_state.texto_p03 = ""


with st.sidebar:
    st.markdown(
        '<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem">// Tu empresa</div>',
        unsafe_allow_html=True,
    )
    empresa = st.text_input("Nombre de tu empresa", placeholder="Ej: Tech Consulting S.L.")
    sector = st.text_input("Sector", placeholder="Ej: Tecnologia y consultoria")
    facturacion = st.selectbox(
        "Facturacion anual",
        ["Menos de 300.000 EUR", "300k - 1M EUR", "1M - 5M EUR", "Mas de 5M EUR"],
    )
    experiencia = st.selectbox(
        "Anos de experiencia", ["Menos de 2", "2-5 anos", "5-10 anos", "Mas de 10 anos"]
    )

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    archivo = st.file_uploader("Sube el pliego (PDF)", type=["pdf"])

    requiere_reindexar = bool(archivo) and (
        archivo.name not in st.session_state.docs_p03 or not st.session_state.texto_p03
    )
    if requiere_reindexar:
        with st.spinner(f"Indexando {archivo.name}..."):
            try:
                bytes_pdf = archivo.read()
                texto_completo, chunks = extraer_todo(bytes_pdf, archivo.name)
                col_db = get_chroma()
                indexar(col_db, chunks, archivo.name)
                st.session_state.texto_p03 = texto_completo
                st.session_state.docs_p03.add(archivo.name)
                st.session_state.analisis_p03 = None
            except Exception as ex:
                st.error(f"No se pudo procesar el PDF: {ex}")
            else:
                st.success(f"Documento indexado: {archivo.name}")

    if st.session_state.docs_p03:
        for d in sorted(st.session_state.docs_p03):
            st.markdown(
                f'<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;padding:.25rem 0">Documento: {d[:40]}</div>',
                unsafe_allow_html=True,
            )

    if st.button("Borrar pliego", use_container_width=True):
        st.cache_resource.clear()
        shutil.rmtree(CHROMA_PATH, ignore_errors=True)
        st.session_state.analisis_p03 = None
        st.session_state.chat_p03 = []
        st.session_state.docs_p03 = set()
        st.session_state.texto_p03 = ""
        st.rerun()

    st.markdown(
        """
    <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
        - Embeddings locales (ChromaDB)<br>
        - El PDF no sale de tu ordenador<br>
        - Analisis y chat libre sobre el pliego
    </div>""",
        unsafe_allow_html=True,
    )

    if not os.getenv("GROQ_API_KEY", "").strip():
        st.warning(
            "Falta GROQ_API_KEY en .env. Podras indexar PDF, pero no analizar ni chatear con IA."
        )


st.markdown(
    """<div class="app-header">
  <div class="app-tag">P03 - Evaluador de licitaciones - Portfolio IA Aplicada
    <span class="groq-badge">Groq - ChromaDB local</span></div>
  <div class="app-title">Evaluador de <em>Licitaciones</em></div>
  <div class="app-subtitle">Sube el pliego - analisis de viabilidad - requisitos - criterios - riesgos - consulta libre</div>
</div>""",
    unsafe_allow_html=True,
)


try:
    col_db = get_chroma()
    total = col_db.count()
except Exception:
    total = 0
    st.error("Error al conectar con ChromaDB. Borra la carpeta chroma_db_p03 y reinicia.")
    st.stop()

if total == 0:
    st.markdown(
        """
    <div style="border:1px dashed rgba(212,168,75,.2);padding:3rem;text-align:center">
      <div style="font-size:2.5rem;margin-bottom:1rem">PDF</div>
      <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:#8c8a84;margin-bottom:.5rem">
        Sube el pliego de condiciones en PDF
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;line-height:1.9">
        Licitaciones SEPE - AEAT - Ayuntamiento - Diputacion - Junta de Andalucia...<br>
        Groq analiza viabilidad, requisitos, criterios y riesgos en segundos
      </div>
    </div>""",
        unsafe_allow_html=True,
    )
    st.stop()

if total > 0 and not st.session_state.docs_p03:
    st.session_state.docs_p03.update(recuperar_fuentes_indexadas(col_db))

if total > 0 and not st.session_state.texto_p03:
    st.info(
        "Hay contexto indexado en Chroma para consultas, pero no hay texto canonico en sesion. "
        "Para un analisis fiel de viabilidad, vuelve a subir el PDF."
    )


if not st.session_state.analisis_p03 and total > 0:
    puede_analizar = bool(st.session_state.texto_p03.strip())
    if st.button(
        "Analizar viabilidad",
        use_container_width=False,
        disabled=not puede_analizar,
        help="Se necesita el texto completo del PDF cargado en la sesion actual.",
    ):
        with st.spinner("Analizando pliego con Groq..."):
            try:
                analisis = analizar_licitacion(
                    get_groq(),
                    st.session_state.texto_p03,
                    empresa,
                    sector,
                    facturacion,
                    experiencia,
                )
                st.session_state.analisis_p03 = analisis
                st.rerun()
            except Exception as ex:
                st.error(f"Error al analizar: {ex}")


if st.session_state.analisis_p03:
    a = st.session_state.analisis_p03
    score = a.get("puntuacion_viabilidad", 5)
    rec = a.get("recomendacion", "-")
    color_rec = {
        "Concursar": "#4dd488",
        "Considerar con cautela": "#d4a84b",
        "No recomendado": "#e87878",
    }.get(rec, "#d4a84b")

    st.markdown(
        f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
        border-bottom:1px solid rgba(212,168,75,.2);padding-bottom:1rem;margin-bottom:1.5rem;flex-wrap:wrap;gap:.75rem">
      <div>
        <span style="font-family:'Fraunces',serif;font-size:1.3rem;font-weight:700">{a.get('titulo_licitacion','Licitacion analizada')}</span>
        <span style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;margin-left:.75rem">{a.get('organismo_convocante','')}</span>
      </div>
      <div style="display:flex;align-items:center;gap:.75rem">
        <span style="font-family:'Fraunces',serif;font-size:2rem;font-weight:900;color:{color_rec}">{score}/10</span>
        <span style="font-family:'DM Mono',monospace;font-size:.72rem;padding:.25rem .75rem;background:rgba(212,168,75,.07);color:{color_rec};border:1px solid {color_rec}40">{rec}</span>
      </div>
    </div>""",
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for col_w, (val, lbl) in zip(
        cols,
        [
            (a.get("presupuesto_base", "-"), "Presupuesto base"),
            (a.get("plazo_ejecucion", "-"), "Plazo de ejecucion"),
            (a.get("fecha_presentacion", "-"), "Fecha limite"),
        ],
    ):
        with col_w:
            st.markdown(
                f"""<div style="background:#14141c;border:1px solid rgba(212,168,75,.12);padding:1rem;text-align:center">
            <div style="font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;color:#d4a84b">{val}</div>
            <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#8c8a84;text-transform:uppercase;letter-spacing:.08em;margin-top:.25rem">{lbl}</div>
            </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="result-block"><div class="result-label">Resumen ejecutivo</div><div style="font-size:.9rem;color:#e4e2dc;line-height:1.85">{a.get("resumen_ejecutivo","")}</div></div>',
        unsafe_allow_html=True,
    )

    col_req, col_ries = st.columns(2)
    with col_req:
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem">Requisitos tecnicos</div>',
            unsafe_allow_html=True,
        )
        for req in a.get("requisitos_tecnicos", []):
            st.markdown(f'<div class="req-item">- {req}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-top:.75rem;margin-bottom:.6rem">Requisitos economicos</div>',
            unsafe_allow_html=True,
        )
        for req in a.get("requisitos_economicos", []):
            st.markdown(f'<div class="req-item">- {req}</div>', unsafe_allow_html=True)
    with col_ries:
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#e87878;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem">Riesgos</div>',
            unsafe_allow_html=True,
        )
        for r_item in a.get("riesgos", []):
            st.markdown(f'<div class="riesgo-item">- {r_item}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#4dd488;text-transform:uppercase;letter-spacing:.1em;margin-top:.75rem;margin-bottom:.6rem">Fortalezas del candidato</div>',
            unsafe_allow_html=True,
        )
        for f in a.get("fortalezas_candidato", []):
            st.markdown(
                f'<div style="padding:.45rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem;color:#a8e8c0">- {f}</div>',
                unsafe_allow_html=True,
            )

    criterios = a.get("criterios_puntuacion", [])
    if criterios:
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem">Criterios de puntuacion</div>',
            unsafe_allow_html=True,
        )
        for crit in criterios:
            if isinstance(crit, dict):
                peso_str = f"{crit.get('peso_pct','')}%" if crit.get("peso_pct") else ""
                st.markdown(
                    f"""<div style="display:flex;justify-content:space-between;padding:.5rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem">
                <span>- {crit.get('criterio', crit)}</span>
                <span style="font-family:'DM Mono',monospace;font-size:.65rem;color:#d4a84b">{peso_str}</span>
                </div>""",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="padding:.45rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem">- {crit}</div>',
                    unsafe_allow_html=True,
                )

    pasos = a.get("proximos_pasos", [])
    if pasos:
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""<div class="result-block"><div class="result-label">Proximos pasos si decides concursar</div>
        {''.join([f"<div style='padding:.5rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem'>{i+1}. {p}</div>" for i,p in enumerate(pasos)])}</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)


st.markdown(
    '<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:.75rem">Consulta el pliego libremente</div>',
    unsafe_allow_html=True,
)

for msg in st.session_state.chat_p03:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-user"><div class="msg-role">Tu</div>{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="msg-bot"><div class="msg-role">Asistente de licitaciones</div>{msg["content"]}</div>',
            unsafe_allow_html=True,
        )

if st.session_state.chat_p03:
    if st.button("Limpiar conversacion"):
        st.session_state.chat_p03 = []
        st.rerun()

col_q, col_btn = st.columns([5, 1])
with col_q:
    pregunta = st.text_input(
        "Pregunta sobre el pliego",
        placeholder="Ej: Cuales son los criterios de adjudicacion? Que documentacion hay que presentar?",
        label_visibility="collapsed",
    )
with col_btn:
    enviar = st.button("Consultar", use_container_width=True)

if enviar and pregunta.strip():
    col_db = get_chroma()
    ctx = buscar(col_db, pregunta.strip())
    if not ctx:
        st.warning("No se encontraron fragmentos relevantes. Reformula la pregunta.")
    else:
        with st.spinner("Consultando pliego..."):
            try:
                resp = responder_consulta(
                    get_groq(), pregunta.strip(), ctx, st.session_state.chat_p03
                )
            except Exception as ex:
                st.error(f"Error en la consulta: {ex}")
            else:
                st.session_state.chat_p03.append(
                    {"role": "user", "content": pregunta.strip()}
                )
                st.session_state.chat_p03.append({"role": "assistant", "content": resp})
                st.rerun()


st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="app-footer">P03 - Evaluador de Licitaciones - Groq + ChromaDB - Portfolio IA Aplicada - Jose Maria - Sevilla</div>',
    unsafe_allow_html=True,
)
