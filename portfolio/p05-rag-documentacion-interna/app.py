"""
P05 - Base publica del motor RAG corporativo multi-dominio
=================================================================
Autor: Jose Maria
Stack: Groq - ChromaDB - sentence-transformers - PyMuPDF - Streamlit

Como funciona:
1. El usuario sube PDFs de documentacion interna.
2. La app extrae el texto, lo divide en fragmentos y lo indexa localmente.
3. ChromaDB recupera los fragmentos mas relevantes para cada pregunta.
4. Groq genera la respuesta apoyandose en esos fragmentos.
5. La app muestra la respuesta y las fuentes consultadas.
"""
import os
import shutil
import time
from pathlib import Path

import chromadb
import fitz
import streamlit as st
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = str(BASE_DIR / "chroma_db")
COLLECTION = "documentacion_empresa"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
TOP_K = 4


st.set_page_config(
    page_title="P05  RAG documental corporativo",
    page_icon="??",
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
.block-container { padding-top:2rem; padding-bottom:2rem; max-width:1100px; }

.app-tag { font-family:'DM Mono',monospace; font-size:.65rem; letter-spacing:.2em; text-transform:uppercase; color:#d4a84b; margin-bottom:.75rem; }
.app-title { font-family:'Fraunces',serif; font-size:2.2rem; font-weight:900; line-height:1.1; margin:0; }
.app-title em { font-style:italic; font-weight:300; color:#d4a84b; }
.app-subtitle { color:#8c8a84; font-size:.9rem; margin-top:.5rem; }
.app-header { border-bottom:1px solid rgba(212,168,75,.2); padding-bottom:1.5rem; margin-bottom:2rem; }

.groq-badge { display:inline-flex; align-items:center; gap:.4rem; font-family:'DM Mono',monospace; font-size:.6rem; color:#4dd488; border:1px solid rgba(77,212,136,.25); padding:.2rem .6rem; margin-left:.75rem; }
.local-badge { display:inline-flex; align-items:center; gap:.4rem; font-family:'DM Mono',monospace; font-size:.6rem; color:#68a8e8; border:1px solid rgba(90,150,212,.25); padding:.2rem .6rem; margin-left:.5rem; }

.stTextInput > label, .stTextArea > label { font-family:'DM Mono',monospace !important; font-size:.7rem !important; letter-spacing:.12em !important; text-transform:uppercase !important; color:#d4a84b !important; }
.stTextInput input, .stTextArea textarea { background:#14141c !important; border:1px solid rgba(212,168,75,.25) !important; border-radius:3px !important; color:#e4e2dc !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color:#d4a84b !important; box-shadow:0 0 0 2px rgba(212,168,75,.1) !important; }

.stButton > button { background:#d4a84b !important; color:#0c0c10 !important; border:none !important; border-radius:3px !important; font-family:'DM Mono',monospace !important; font-size:.75rem !important; font-weight:700 !important; letter-spacing:.1em !important; text-transform:uppercase !important; padding:.65rem 2rem !important; transition:all .2s !important; }
.stButton > button:hover { background:#e8c97a !important; transform:translateY(-1px); box-shadow:0 4px 20px rgba(212,168,75,.3) !important; }
button[data-testid="baseButton-secondary"] { background:transparent !important; color:var(--text-2) !important; border:1px solid rgba(212,168,75,.25) !important; }

.answer-box {
    background:#14141c;
    border:1px solid rgba(212,168,75,.2);
    padding:1.75rem 2rem;
    margin-bottom:1.5rem;
    position:relative;
}
.answer-box::before {
    content:'';
    position:absolute;
    top:0; left:0;
    width:3px; height:100%;
    background:linear-gradient(180deg,#d4a84b,transparent);
}
.answer-label {
    font-family:'DM Mono',monospace;
    font-size:.62rem;
    letter-spacing:.12em;
    text-transform:uppercase;
    color:#7a5e28;
    margin-bottom:.75rem;
}
.answer-text {
    font-size:.95rem;
    color:#e4e2dc;
    line-height:1.85;
}

.source-box {
    border:1px solid rgba(212,168,75,.1);
    background:#0f0f18;
    padding:1rem 1.25rem;
    margin-bottom:.6rem;
}
.source-header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:.5rem;
}
.source-file {
    font-family:'DM Mono',monospace;
    font-size:.62rem;
    color:#d4a84b;
    letter-spacing:.08em;
}
.source-page {
    font-family:'DM Mono',monospace;
    font-size:.6rem;
    color:#44433f;
}
.source-text {
    font-size:.8rem;
    color:#8c8a84;
    line-height:1.7;
}

.hist-user {
    background:rgba(212,168,75,.06);
    border:1px solid rgba(212,168,75,.12);
    padding:1rem 1.25rem;
    margin-bottom:.5rem;
    font-size:.875rem;
}
.hist-assistant {
    background:#14141c;
    border:1px solid rgba(212,168,75,.1);
    padding:1rem 1.25rem;
    margin-bottom:1rem;
    font-size:.875rem;
    color:#c8c6c0;
    line-height:1.8;
}
.hist-role {
    font-family:'DM Mono',monospace;
    font-size:.58rem;
    color:#44433f;
    letter-spacing:.1em;
    text-transform:uppercase;
    margin-bottom:.4rem;
}

.doc-item {
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:.6rem .75rem;
    border:1px solid rgba(212,168,75,.1);
    margin-bottom:.4rem;
    font-size:.8rem;
}
.doc-name { color:#c8c6c0; }
.doc-chunks {
    font-family:'DM Mono',monospace;
    font-size:.62rem;
    color:#44433f;
}

.chip {
    display:inline-block;
    font-family:'DM Mono',monospace;
    font-size:.6rem;
    padding:.25rem .7rem;
    border:1px solid rgba(212,168,75,.15);
    color:#8c8a84;
    margin:.2rem;
}

.custom-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent); margin:1.5rem 0; }
.app-footer { font-family:'DM Mono',monospace; font-size:.62rem; color:#44433f; text-align:center; padding-top:2rem; }
[data-testid="stSidebar"] { background:#10101a !important; border-right:1px solid rgba(212,168,75,.12) !important; }
.streamlit-expanderHeader { font-family:'DM Mono',monospace !important; color:#d4a84b !important; background:#14141c !important; border:1px solid rgba(212,168,75,.2) !important; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_chroma():
    """Inicializa ChromaDB con embeddings locales."""
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


@st.cache_resource
def get_groq() -> Groq:
    """Crea el cliente de Groq si la API key est disponible."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y aade tu clave antes de hacer consultas."
        )
    return Groq(api_key=api_key)


def extraer_texto_pdf(archivo_bytes: bytes, nombre: str) -> list[dict]:
    """Extrae texto del PDF y lo divide en fragmentos con metadatos."""
    try:
        doc = fitz.open(stream=archivo_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"No se pudo abrir el PDF '{nombre}'.") from exc

    chunks = []
    try:
        for num_pag, pagina in enumerate(doc, start=1):
            texto = pagina.get_text("text").strip()
            if not texto:
                continue

            inicio = 0
            while inicio < len(texto):
                fin = inicio + CHUNK_SIZE
                chunk = texto[inicio:fin].strip()
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
            f"No se pudo extraer texto til de '{nombre}'. Comprueba que no sea un PDF escaneado sin texto seleccionable."
        )

    return chunks


def indexar_documento(collection, chunks: list[dict], nombre: str):
    """Aade los fragmentos del documento a ChromaDB."""
    try:
        ids_existentes = collection.get(where={"fuente": nombre})["ids"]
        if ids_existentes:
            collection.delete(ids=ids_existentes)
    except Exception:
        pass

    if not chunks:
        return 0

    collection.upsert(
        documents=[c["texto"] for c in chunks],
        ids=[c["id"] for c in chunks],
        metadatas=[{"fuente": c["fuente"], "pagina": c["pagina"]} for c in chunks],
    )
    return len(chunks)


def buscar_contexto(collection, pregunta: str, k: int = TOP_K) -> list[dict]:
    """Recupera los fragmentos ms relevantes para la pregunta."""
    total = collection.count()
    if total == 0:
        return []

    resultados = collection.query(
        query_texts=[pregunta],
        n_results=min(k, total),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    if resultados and resultados["documents"]:
        for doc, meta, dist in zip(
            resultados["documents"][0],
            resultados["metadatas"][0],
            resultados["distances"][0],
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


def generar_respuesta(groq_client, pregunta: str, contexto: list[dict], historial: list, empresa: str = "") -> str:
    """Genera una respuesta a partir del contexto recuperado."""
    contexto_str = "\n\n---\n\n".join(
        [f"[Fuente: {c['fuente']}, Pg. {c['pagina']}]\n{c['texto']}" for c in contexto]
    )

    empresa_str = f" de {empresa}" if empresa else ""
    system = (
        f"Eres un asistente de documentacin interna{empresa_str}. "
        "Responde a partir de los fragmentos recuperados del repositorio documental. "
        "Si la informacin no aparece con suficiente respaldo en el contexto, di exactamente: "
        "'No encuentro esa informacin con suficiente respaldo en la documentacin disponible.' "
        "Responde en espaol, de forma clara y directa. "
        "Cita siempre el documento y la pgina cuando sea posible."
    )

    mensajes = [{"role": "system", "content": system}]
    for msg in historial[-4:]:
        mensajes.append(msg)
    mensajes.append(
        {
            "role": "user",
            "content": f"DOCUMENTOS RECUPERADOS:\n{contexto_str}\n\nPREGUNTA: {pregunta}",
        }
    )

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=mensajes,
        temperature=0.1,
        max_tokens=1000,
    )
    contenido = response.choices[0].message.content
    if not contenido:
        raise ValueError("El modelo no devolvi una respuesta utilizable.")
    return contenido


def get_docs_indexados(collection) -> dict:
    """Devuelve los documentos indexados con su nmero de fragmentos."""
    if collection.count() == 0:
        return {}
    todos = collection.get(include=["metadatas"])
    conteo = {}
    for meta in todos["metadatas"]:
        fuente = meta.get("fuente", "")
        conteo[fuente] = conteo.get(fuente, 0) + 1
    return conteo


if "historial" not in st.session_state:
    st.session_state.historial = []
if "docs_procesados" not in st.session_state:
    st.session_state.docs_procesados = set()

with st.sidebar:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem\">// Cargar documentos</div>",
        unsafe_allow_html=True,
    )

    nombre_empresa = st.text_input(
        "Nombre de la empresa (opcional)",
        placeholder="Ej: Acme S.L.",
    )

    archivos = st.file_uploader(
        "Sube PDFs de la empresa",
        type=["pdf"],
        accept_multiple_files=True,
        help="Manuales, procedimientos, polticas, organigramas, FAQs y otras guas internas.",
    )

    if archivos:
        try:
            collection = get_chroma()
        except Exception as exc:
            st.error("No se pudo inicializar la base vectorial local.")
            with st.expander("Ver detalle tcnico"):
                st.code(str(exc))
            st.stop()

        for archivo in archivos:
            if archivo.name not in st.session_state.docs_procesados:
                with st.spinner(f"Procesando {archivo.name}..."):
                    try:
                        chunks = extraer_texto_pdf(archivo.read(), archivo.name)
                        n_chunks = indexar_documento(collection, chunks, archivo.name)
                        st.session_state.docs_procesados.add(archivo.name)
                        st.success(f"{archivo.name}  {n_chunks} fragmentos indexados")
                    except Exception as exc:
                        st.error(f"No se pudo procesar {archivo.name}.")
                        with st.expander(f"Ver detalle tcnico: {archivo.name}"):
                            st.code(str(exc))

    try:
        collection = get_chroma()
        docs = get_docs_indexados(collection)
        if docs:
            st.markdown(
                "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;margin:1.25rem 0 .75rem\">// Documentos indexados</div>",
                unsafe_allow_html=True,
            )
            for nombre, n in docs.items():
                st.markdown(
                    f"""
                <div class="doc-item">
                  <span class="doc-name">?? {nombre[:28]}{'' if len(nombre) > 28 else ''}</span>
                  <span class="doc-chunks">{n} frags</span>
                </div>""",
                    unsafe_allow_html=True,
                )

            total = sum(docs.values())
            st.markdown(
                f"<div style=\"font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;margin-top:.5rem\">{len(docs)} docs  {total} fragmentos totales</div>",
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
            if st.button("Borrar toda la base", use_container_width=True):
                try:
                    client = chromadb.PersistentClient(
                        path=CHROMA_PATH,
                        settings=Settings(anonymized_telemetry=False),
                    )
                    client.delete_collection(COLLECTION)
                except Exception:
                    pass
                st.cache_resource.clear()
                st.session_state.docs_procesados = set()
                st.session_state.historial = []
                time.sleep(0.3)
                shutil.rmtree(CHROMA_PATH, ignore_errors=True)
                st.rerun()
    except Exception:
        pass

    st.markdown(
        """
    <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;
        line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
        <span style="color:#4dd488">?</span> Embeddings e indexado: local<br>
        <span style="color:#4dd488">?</span> Base vectorial: ChromaDB en disco<br>
        <span style="color:#4dd488">?</span> Respuesta: Groq con fragmentos recuperados<br>
        <span style="color:#d4a84b">?</span> Base pblica actual del motor RAG corporativo
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:.58rem;color:#44433f;margin-top:1.5rem">
        P05  Portfolio IA Aplicada<br>
        <a href="https://github.com/chema74/portfolio-ia-aplicada/tree/main/portfolio/p05-rag-documentacion-interna" style="color:#7a5e28">Ver proyecto en GitHub ?</a>
    </div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
<div class="app-header">
  <div class="app-tag">P05  Base pblica actual  Motor RAG corporativo multi-dominio
    <span class="groq-badge">? Groq  Llama 3.3 70B</span>
    <span class="local-badge">?? ChromaDB local</span>
  </div>
  <div class="app-title">Asistente <em>documental</em>{f'  {nombre_empresa}' if nombre_empresa else ''}</div>
  <div class="app-subtitle">
    Consulta documentacin interna con RAG local y respuestas apoyadas en fragmentos recuperados.
  </div>
</div>""",
    unsafe_allow_html=True,
)

st.info(
    "La indexacin y la base vectorial se gestionan localmente. Para responder, la app enva al modelo la pregunta y los fragmentos recuperados como contexto."
)

try:
    collection = get_chroma()
    total_docs = collection.count()
except Exception as exc:
    st.error("No se pudo abrir la base documental local.")
    with st.expander("Ver detalle tcnico"):
        st.code(str(exc))
    st.stop()

if total_docs == 0:
    st.markdown(
        """
    <div style="border:1px dashed rgba(212,168,75,.2);padding:3rem 2rem;text-align:center;margin-top:1rem">
      <div style="font-size:2.5rem;margin-bottom:1rem">??</div>
      <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#8c8a84;margin-bottom:.75rem">
        Sube los PDFs de tu empresa para empezar
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:.63rem;color:#44433f;letter-spacing:.06em;line-height:2">
        Ejemplos: manual de empleado  procedimientos  polticas de RR. HH.<br>
        organigramas  FAQs internas  normativa  guas de producto<br>
        <span style="color:#4dd488">La indexacin se hace en local y la respuesta se apoya en fragmentos recuperados de tus documentos.</span>
      </div>
    </div>""",
        unsafe_allow_html=True,
    )
    st.stop()

sugerencias = [
    "Cuntos das de vacaciones tengo al ao?",
    "Cul es el procedimiento para solicitar una baja?",
    "A quin tengo que dirigirme para reportar una incidencia de IT?",
    "Cules son los horarios de trabajo?",
    "Qu herramientas usa el equipo de ventas?",
    "Resume los valores y misin de la empresa.",
]

st.markdown(
    "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;margin-bottom:.6rem\">Preguntas de ejemplo</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "".join([f'<span class="chip">{s}</span>' for s in sugerencias]),
    unsafe_allow_html=True,
)
st.caption("Son ejemplos de consulta. Puedes escribir tu propia pregunta en el cuadro inferior.")

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

if st.session_state.historial:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;margin-bottom:.75rem\">// Conversacin</div>",
        unsafe_allow_html=True,
    )

    for msg in st.session_state.historial:
        if msg["role"] == "user":
            st.markdown(
                f"""
            <div class="hist-user">
              <div class="hist-role">T</div>
              {msg["content"]}
            </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="hist-assistant">
              <div class="hist-role">Asistente documental</div>
              {msg["content"]}
            </div>""",
                unsafe_allow_html=True,
            )

    if st.button("Limpiar conversacin", use_container_width=False):
        st.session_state.historial = []
        st.rerun()

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

col_q, col_btn = st.columns([5, 1])
with col_q:
    pregunta = st.text_input(
        "Escribe tu pregunta",
        placeholder="Ej: Cuntos das de vacaciones tengo? Cul es el proceso de onboarding?",
        key="input_pregunta",
    )
with col_btn:
    st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
    preguntar = st.button("Preguntar ?", use_container_width=True)

if preguntar and pregunta.strip():
    try:
        collection = get_chroma()
    except Exception as exc:
        st.error("No se pudo abrir la base vectorial local para consultar documentos.")
        with st.expander("Ver detalle tcnico"):
            st.code(str(exc))
        st.stop()

    try:
        groq_client = get_groq()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    if collection.count() == 0:
        st.warning("No hay documentos indexados. Sube PDFs primero.")
        st.stop()

    with st.spinner("Buscando en los documentos..."):
        try:
            contexto = buscar_contexto(collection, pregunta.strip())
        except Exception as exc:
            st.error("No se pudo recuperar contexto desde la base documental.")
            with st.expander("Ver detalle tcnico"):
                st.code(str(exc))
            st.stop()

    if not contexto:
        st.warning("No se encontraron fragmentos relevantes. Intenta reformular la pregunta.")
        st.stop()

    with st.spinner("Generando respuesta con Groq..."):
        try:
            respuesta = generar_respuesta(
                groq_client,
                pregunta.strip(),
                contexto,
                st.session_state.historial,
                nombre_empresa,
            )
        except Exception as exc:
            st.error("No se pudo generar una respuesta a partir del contexto recuperado.")
            with st.expander("Ver detalle tcnico"):
                st.code(str(exc))
            st.stop()

    st.markdown(
        f"""
    <div class="answer-box">
      <div class="answer-label">Respuesta apoyada en fragmentos recuperados</div>
      <div class="answer-text">{respuesta}</div>
    </div>""",
        unsafe_allow_html=True,
    )

    with st.expander(f"Ver fuentes consultadas ({len(contexto)} fragmentos)"):
        for chunk in contexto:
            st.markdown(
                f"""
            <div class="source-box">
              <div class="source-header">
                <span class="source-file">?? {chunk['fuente']}</span>
                <span class="source-page">Pg. {chunk['pagina']}  Relevancia: {chunk['score']:.0%}</span>
              </div>
              <div class="source-text">{chunk['texto'][:300]}{'' if len(chunk['texto']) > 300 else ''}</div>
            </div>""",
                unsafe_allow_html=True,
            )

    st.session_state.historial.append({"role": "user", "content": pregunta.strip()})
    st.session_state.historial.append({"role": "assistant", "content": respuesta})

elif preguntar and not pregunta.strip():
    st.warning("Escribe una pregunta.")

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="app-footer">P05  Base pblica actual del motor RAG corporativo multi-dominio  Groq + ChromaDB local + sentence-transformers  Portfolio IA Aplicada  Jos Mara  Sevilla</div>',
    unsafe_allow_html=True,
)

