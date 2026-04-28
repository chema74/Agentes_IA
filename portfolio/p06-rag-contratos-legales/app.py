"""
P07  Revisor de contratos legales
=================================
Autor: Jose Maria
Stack: Groq  ChromaDB  sentence-transformers  PyMuPDF  Streamlit

Como funciona:
1. El usuario sube uno o varios PDFs.
2. La app extrae texto y lo indexa localmente con ChromaDB.
3. El usuario hace preguntas sobre clausulas, plazos, obligaciones o riesgos detectables en el texto.
4. La app recupera fragmentos relevantes y Groq responde a partir de ellos.
5. La salida es una revision asistida, no asesoramiento juridico profesional.
"""

import os
import shutil
import time
from pathlib import Path

import chromadb
import fitz
import streamlit as st
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = str(BASE_DIR / "chroma_db_p06")
COLLECTION = "contratos"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K = 5

PREGUNTAS_RAPIDAS = [
    "Cuales son las clausulas mas importantes de este contrato?",
    "Que riesgos o clausulas sensibles detectas en el texto?",
    "Cuales son las obligaciones de cada parte?",
    "Que plazos y fechas clave aparecen en el documento?",
    "Que condiciones de rescision o penalizacion se recogen?",
    "Resume el documento en 5 puntos clave.",
]


st.set_page_config(
    page_title="Revisor de contratos legales",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,300&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:#0c0c10;color:#e4e2dc}
.stApp{background:#0c0c10}#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:2rem;padding-bottom:2rem;max-width:1000px}
.app-tag{font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;color:#d4a84b;margin-bottom:.75rem}
.app-title{font-family:'Fraunces',serif;font-size:2.2rem;font-weight:900;line-height:1.1;margin:0}
.app-title em{font-style:italic;font-weight:300;color:#d4a84b}
.app-subtitle{color:#8c8a84;font-size:.9rem;margin-top:.5rem}
.app-header{border-bottom:1px solid rgba(212,168,75,.2);padding-bottom:1.5rem;margin-bottom:2rem}
.groq-badge{display:inline-flex;align-items:center;gap:.4rem;font-family:'DM Mono',monospace;font-size:.6rem;color:#4dd488;border:1px solid rgba(77,212,136,.25);padding:.2rem .6rem;margin-left:.75rem}
.stTextInput>label,.stTextArea>label{font-family:'DM Mono',monospace !important;font-size:.7rem !important;letter-spacing:.12em !important;text-transform:uppercase !important;color:#d4a84b !important}
.stTextInput input,.stTextArea textarea{background:#14141c !important;border:1px solid rgba(212,168,75,.25) !important;border-radius:3px !important;color:#e4e2dc !important}
.stButton>button{background:#d4a84b !important;color:#0c0c10 !important;border:none !important;border-radius:3px !important;font-family:'DM Mono',monospace !important;font-size:.75rem !important;font-weight:700 !important;letter-spacing:.1em !important;text-transform:uppercase !important;padding:.65rem 2rem !important}
.stButton>button:hover{background:#e8c97a !important;transform:translateY(-1px)}
.msg-user{background:rgba(212,168,75,.06);border:1px solid rgba(212,168,75,.12);padding:.9rem 1.1rem;margin-bottom:.4rem;font-size:.875rem}
.msg-bot{background:#14141c;border:1px solid rgba(212,168,75,.1);border-left:3px solid #d4a84b;padding:1.1rem 1.4rem;margin-bottom:.75rem;font-size:.875rem;line-height:1.85;color:#e4e2dc}
.msg-role{font-family:'DM Mono',monospace;font-size:.58rem;color:#44433f;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.35rem}
.custom-divider{height:1px;background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent);margin:1.5rem 0}
.app-footer{font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;text-align:center;padding-top:2rem}
.chip{display:inline-block;font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.15);color:#8c8a84;margin:.2rem}
[data-testid="stSidebar"]{background:#10101a !important;border-right:1px solid rgba(212,168,75,.12) !important}
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
            "Falta GROQ_API_KEY. Copia .env.example a .env y anade tu clave antes de analizar documentos."
        )
    return Groq(api_key=api_key)


@st.cache_resource
def get_chroma():
    """Inicializa la coleccion persistente de Chroma."""
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )  # type: ignore[arg-type]


def extraer_chunks(bytes_pdf, nombre):
    """Extrae texto del PDF y lo divide en fragmentos indexables."""
    try:
        doc = fitz.open(stream=bytes_pdf, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"No se pudo abrir el PDF '{nombre}'.") from exc

    chunks = []
    try:
        for num_pag, pag in enumerate(doc, 1):  # type: ignore
            texto = pag.get_text("text").strip()
            if not texto:
                continue
            inicio = 0
            while inicio < len(texto):
                chunk = texto[inicio:inicio + CHUNK_SIZE].strip()
                if len(chunk) > 50:
                    chunks.append(
                        {
                            "texto": chunk,
                            "fuente": nombre,
                            "pagina": num_pag,
                            "id": f"{nombre}_p{num_pag}_c{inicio}",
                        }
                    )
                inicio += CHUNK_SIZE - CHUNK_OVERLAP
    finally:
        doc.close()

    if not chunks:
        raise ValueError(
            f"No se pudo extraer texto util del PDF '{nombre}'. Comprueba que no sea una imagen escaneada sin texto seleccionable."
        )

    return chunks


def indexar(collection, chunks, nombre):
    """Elimina versiones previas e indexa el documento en Chroma."""
    try:
        ids = collection.get(where={"fuente": nombre})["ids"]
        if ids:
            collection.delete(ids=ids)
    except Exception:
        pass

    collection.upsert(
        documents=[c["texto"] for c in chunks],
        ids=[c["id"] for c in chunks],
        metadatas=[{"fuente": c["fuente"], "pagina": c["pagina"]} for c in chunks],
    )
    return len(chunks)


def buscar(collection, pregunta, k=TOP_K):
    """Recupera los fragmentos mas relevantes para la pregunta."""
    if collection.count() == 0:
        return []

    respuesta = collection.query(
        query_texts=[pregunta],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    if respuesta and respuesta["documents"]:
        for doc, meta, dist in zip(
            respuesta["documents"][0],
            respuesta["metadatas"][0],
            respuesta["distances"][0],
        ):
            chunks.append(
                {
                    "texto": doc,
                    "fuente": meta.get("fuente", ""),
                    "pagina": meta.get("pagina", ""),
                    "score": round(1 - dist, 3),
                }
            )
    return chunks


def responder(groq_client, pregunta, contexto, historial, tipo_doc):
    """Genera una respuesta a partir del contexto recuperado."""
    ctx_str = "\n\n---\n\n".join(
        [f"[{c['fuente']}, Pag. {c['pagina']}]\n{c['texto']}" for c in contexto]
    )
    system = (
        f"Eres un asistente de revision documental especializado en {tipo_doc}. "
        "Responde solo a partir del contenido recuperado del documento. "
        "Si identificas clausulas sensibles, riesgos, obligaciones o plazos, destacalos con lenguaje claro. "
        "Cita siempre la pagina cuando sea posible. "
        "No afirmes que sustituyes revision juridica profesional. "
        "Responde en espanol."
    )
    mensajes = [{"role": "system", "content": system}]
    for mensaje in historial[-4:]:
        mensajes.append({"role": mensaje["role"], "content": mensaje["content"]})
    mensajes.append(
        {
            "role": "user",
            "content": f"DOCUMENTO:\n{ctx_str}\n\nPREGUNTA: {pregunta}",
        }
    )

    respuesta = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=mensajes,
        temperature=0.1,
        max_tokens=900,
    )
    contenido = respuesta.choices[0].message.content
    if not contenido:
        raise ValueError("El modelo no devolvio una respuesta utilizable.")
    return contenido


if "historial_p07" not in st.session_state:
    st.session_state.historial_p07 = []
if "docs_p07" not in st.session_state:
    st.session_state.docs_p07 = set()

with st.sidebar:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem\">// Cargar documento</div>",
        unsafe_allow_html=True,
    )
    tipo_doc = st.selectbox(
        "Tipo de documento",
        [
            "Contrato",
            "Acuerdo comercial",
            "Convenio",
            "Normativa",
            "Pliego de condiciones",
            "Otro documento legal",
        ],
    )
    archivos = st.file_uploader("Sube uno o varios PDF", type=["pdf"], accept_multiple_files=True)

    if archivos:
        try:
            coleccion = get_chroma()
        except Exception as exc:
            st.error("No se pudo inicializar la base documental local.")
            with st.expander("Ver detalle tecnico"):
                st.code(str(exc))
            st.stop()

        for archivo in archivos:
            if archivo.name not in st.session_state.docs_p07:
                with st.spinner(f"Indexando {archivo.name}..."):
                    try:
                        chunks = extraer_chunks(archivo.read(), archivo.name)
                        total_chunks = indexar(coleccion, chunks, archivo.name)
                        st.session_state.docs_p07.add(archivo.name)
                        st.success(f"{archivo.name} indexado ({total_chunks} fragmentos).")
                    except Exception as exc:
                        st.error(f"No se pudo indexar {archivo.name}.")
                        with st.expander(f"Detalle tecnico: {archivo.name}"):
                            st.code(str(exc))

    if st.session_state.docs_p07:
        for documento in st.session_state.docs_p07:
            st.markdown(
                f"<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;color:#7a5e28;padding:.3rem 0\"> {documento[:40]}</div>",
                unsafe_allow_html=True,
            )

    if st.button("Borrar documentos", use_container_width=True):
        st.cache_resource.clear()
        time.sleep(0.3)
        shutil.rmtree(CHROMA_PATH, ignore_errors=True)
        st.session_state.docs_p07 = set()
        st.session_state.historial_p07 = []
        st.rerun()

    st.markdown(
        """
<div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
<span style="color:#4dd488"></span> Embeddings e indexado locales<br>
<span style="color:#4dd488"></span> Se envian al modelo solo fragmentos relevantes recuperados<br>
<span style="color:#d4a84b"></span> Revisin asistida, no asesoramiento juridico
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="app-header">
  <div class="app-tag">P07  Revisor de contratos legales  Portfolio IA Aplicada
    <span class="groq-badge"> Groq  ChromaDB local</span></div>
  <div class="app-title">Revisor de <em>contratos legales</em></div>
  <div class="app-subtitle">Sube el PDF y consulta clausulas, obligaciones, plazos, penalizaciones o riesgos detectables en el texto.</div>
</div>
""",
    unsafe_allow_html=True,
)

st.info(
    "Esta app ayuda a revisar documentos legales a partir del texto recuperado. No sustituye la revision juridica profesional ni emite dictamenes legales."
)

try:
    coleccion = get_chroma()
    total = coleccion.count()
except Exception as exc:
    st.error("No se pudo abrir la base documental local.")
    with st.expander("Ver detalle tecnico"):
        st.code(str(exc))
    st.stop()

if total == 0:
    st.markdown(
        """
    <div style="border:1px dashed rgba(212,168,75,.2);padding:3rem;text-align:center">
    <div style="font-size:2.5rem;margin-bottom:1rem"></div>
    <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:#8c8a84">Sube el contrato o documento legal en el panel izquierdo para empezar</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem\">Preguntas frecuentes</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "".join([f'<span class="chip">{pregunta}</span>' for pregunta in PREGUNTAS_RAPIDAS]),
    unsafe_allow_html=True,
)
st.caption("Son ejemplos de consulta. Escribe tu pregunta en el campo inferior.")
st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

for mensaje in st.session_state.historial_p07:
    if mensaje["role"] == "user":
        st.markdown(
            f'<div class="msg-user"><div class="msg-role">T</div>{mensaje["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="msg-bot"><div class="msg-role">Asistente documental</div>{mensaje["content"]}</div>',
            unsafe_allow_html=True,
        )

if st.session_state.historial_p07:
    if st.button("Limpiar conversacion"):
        st.session_state.historial_p07 = []
        st.rerun()
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

col_q, col_btn = st.columns([5, 1])
with col_q:
    pregunta = st.text_input(
        "Tu pregunta sobre el documento",
        placeholder="Ej: Que clausulas pueden suponer un riesgo para mi empresa?",
        label_visibility="collapsed",
    )
with col_btn:
    enviar = st.button("Preguntar ", use_container_width=True)

if enviar and pregunta.strip():
    contexto = buscar(coleccion, pregunta.strip())
    if not contexto:
        st.warning("No se encontraron fragmentos relevantes para esa pregunta.")
    else:
        try:
            groq_client = get_groq()
        except Exception as exc:
            st.error(str(exc))
            st.stop()

        with st.spinner("Analizando el documento..."):
            try:
                respuesta = responder(
                    groq_client,
                    pregunta.strip(),
                    contexto,
                    st.session_state.historial_p07,
                    tipo_doc,
                )
            except Exception as exc:
                st.error("No se pudo generar una respuesta sobre el documento.")
                with st.expander("Ver detalle tecnico"):
                    st.code(str(exc))
                st.stop()

        st.session_state.historial_p07.append({"role": "user", "content": pregunta.strip()})
        st.session_state.historial_p07.append({"role": "assistant", "content": respuesta})
        st.rerun()

elif enviar and not pregunta.strip():
    st.warning("Escribe una pregunta antes de consultar el documento.")

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="app-footer">P07  Revisor de contratos legales  Groq + ChromaDB  Portfolio IA Aplicada  Jose Maria  Sevilla</div>',
    unsafe_allow_html=True,
)
