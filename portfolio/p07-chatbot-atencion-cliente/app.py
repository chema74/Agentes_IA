"""
P07 - Chatbot de atencion al cliente con RAG y memoria
=======================================================
Autor : Jose Maria  |  Sevilla 2026
Stack : Groq - ChromaDB - sentence-transformers - PyMuPDF - Streamlit

Como funciona:
1. Sube la base de conocimiento de tu empresa en PDF.
2. La app extrae texto, lo indexa localmente con ChromaDB y embeddings.
3. El chatbot recupera los fragmentos mas relevantes para cada pregunta.
4. Groq genera una respuesta basada en esos fragmentos con memoria de conversacion.
5. Si la pregunta no tiene respaldo documental, el bot sugiere escalar a una persona.

Limites:
- Responde solo con lo que encuentra en los documentos cargados.
- No sustituye a un agente humano cuando la situacion lo requiere.
- Para un chatbot de produccion consulta la version producto del repositorio.
"""

import os
import shutil
import time
from pathlib import Path
from typing import List, Tuple, Dict

import chromadb
import fitz  # PyMuPDF
import streamlit as st
from chromadb.config import Settings
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = str(BASE_DIR / "chroma_db_p07")
COLLECTION_NAME = "atencion_cliente"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# ── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="P07 - Chatbot de atencion al cliente",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
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

.msg-user { background:rgba(212,168,75,.06); border:1px solid rgba(212,168,75,.12); padding:.9rem 1.1rem; margin-bottom:.4rem; font-size:.875rem; }
.msg-bot { background:#14141c; border:1px solid rgba(212,168,75,.1); border-left:3px solid #d4a84b; padding:1.1rem 1.4rem; margin-bottom:.75rem; font-size:.875rem; line-height:1.85; color:#e4e2dc; }
.msg-escalate { background:rgba(232,120,120,.06); border:1px solid rgba(232,120,120,.2); border-left:3px solid #e87878; padding:.75rem 1.1rem; margin-bottom:.75rem; font-size:.82rem; color:#e8b8b8; }
.msg-role { font-family:'DM Mono',monospace; font-size:.58rem; color:#44433f; letter-spacing:.1em; text-transform:uppercase; margin-bottom:.35rem; }

.source-box { background:#0a0a0f; border:1px solid rgba(212,168,75,.1); padding:.75rem 1rem; margin-bottom:.4rem; font-size:.78rem; color:#8c8a84; }
.doc-item { display:flex; align-items:center; justify-content:space-between; padding:.6rem .75rem; border:1px solid rgba(212,168,75,.1); margin-bottom:.4rem; font-size:.8rem; }
.doc-name { color:#c8c6c0; }
.doc-chunks { font-family:'DM Mono',monospace; font-size:.62rem; color:#44433f; }

.custom-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent); margin:1.5rem 0; }
.app-footer { font-family:'DM Mono',monospace; font-size:.62rem; color:#44433f; text-align:center; padding-top:2rem; }
[data-testid="stSidebar"] { background:#10101a !important; border-right:1px solid rgba(212,168,75,.12) !important; }
</style>
""", unsafe_allow_html=True)


# ── RECURSOS CACHEADOS ───────────────────────────────────────────────────────
@st.cache_resource
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL_NAME)


@st.cache_resource
def get_chroma_client():
    return chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection():
    return get_chroma_client().get_or_create_collection(name=COLLECTION_NAME)


@st.cache_resource
def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y anade tu clave antes de usar el chatbot."
        )
    return Groq(api_key=api_key)


# ── PROCESAMIENTO DE PDFs ────────────────────────────────────────────────────
def extract_text_from_pdf(file) -> List[Tuple[int, str]]:
    """Extrae texto pagina a pagina del PDF."""
    pages = []
    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for i, page in enumerate(pdf):  # type: ignore
            text = page.get_text("text").strip()
            if text:
                pages.append((i + 1, text))
        pdf.close()
    except Exception as exc:
        st.error(f"Error leyendo PDF {file.name}: {exc}")
    return pages


def split_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Divide el texto en fragmentos sin cortar palabras."""
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space != -1:
                end = last_space
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 50]


def index_pdf(uploaded_file) -> int:
    """Indexa un PDF en ChromaDB con embeddings locales."""
    collection = get_or_create_collection()
    embedder = get_embedder()
    pages = extract_text_from_pdf(uploaded_file)
    if not pages:
        return 0

    docs, ids, metadatas = [], [], []
    for page_num, page_text in pages:
        for idx, chunk in enumerate(split_text(page_text)):
            doc_id = f"{uploaded_file.name}_p{page_num}_c{idx}"
            docs.append(chunk)
            ids.append(doc_id)
            metadatas.append({"source": uploaded_file.name, "page": page_num})

    if docs:
        embeddings = embedder.encode(docs).tolist()  # type: ignore
        collection.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)

    return len(docs)


# ── RAG + MEMORIA ────────────────────────────────────────────────────────────
def search_context(query: str, k: int = 4) -> List[Tuple[str, Dict]]:
    """Recupera los fragmentos mas relevantes para la pregunta."""
    collection = get_or_create_collection()
    if collection.count() == 0:
        return []
    embedder = get_embedder()
    query_embedding = embedder.encode([query]).tolist()[0]  # type: ignore
    results = collection.query(query_embeddings=[query_embedding], n_results=min(k, collection.count()))
    if not results["documents"] or not results["documents"][0]:
        return []
    return list(zip(results["documents"][0], results["metadatas"][0]))  # type: ignore


def generate_answer(
    question: str,
    history: List[Dict],
    tone: str,
    channel: str,
) -> Tuple[str, List[Tuple[str, Dict]], bool]:
    """Genera respuesta con RAG y memoria de conversacion."""
    context_items = search_context(question)
    context_text = "\n".join(
        [f"[Doc: {m['source']} pag.{m['page']}]: {d}" for d, m in context_items]
    )

    memory_messages = []
    for turn in history[-4:]:
        memory_messages.append({"role": "user", "content": turn["question"]})
        memory_messages.append({"role": "assistant", "content": turn["answer"]})

    system_prompt = (
        f"Eres un asistente de atencion al cliente. Tono: {tone}. Canal: {channel}.\n"
        "REGLAS:\n"
        "1. Usa SOLO el contenido de los documentos cargados.\n"
        "2. Si no encuentras informacion suficiente, di claramente que no tienes esa informacion "
        "y sugiere hablar con una persona del equipo.\n"
        "3. Recuerda el contexto de la conversacion previa para responder preguntas de seguimiento.\n"
        "4. Cita el documento y la pagina al final de cada respuesta.\n"
        "5. Responde en espanol.\n"
        f"\nCONTEXTO RECUPERADO:\n{context_text}"
    )

    messages = (
        [{"role": "system", "content": system_prompt}]
        + memory_messages
        + [{"role": "user", "content": question}]
    )

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,  # type: ignore
            temperature=0.15,
            max_tokens=700,
        )
        answer = response.choices[0].message.content or ""

        # Logica de escalado a agente humano
        low_conf_keywords = [
            "no tengo informacion",
            "no encuentro",
            "no aparece",
            "no puedo confirmar",
            "hablar con",
            "contactar con",
        ]
        escalate = (
            any(kw in answer.lower() for kw in low_conf_keywords)
            or len(context_items) == 0
        )

        return answer, context_items, escalate

    except Exception as exc:
        return f"Error al generar respuesta: {exc}", [], True


def get_docs_indexados() -> Dict[str, int]:
    """Devuelve documentos indexados con su numero de fragmentos."""
    try:
        collection = get_or_create_collection()
        if collection.count() == 0:
            return {}
        todos = collection.get(include=["metadatas"])
        conteo: Dict[str, int] = {}
        for meta in todos["metadatas"]:  # type: ignore
            src = meta.get("source", "")
            conteo[src] = conteo.get(src, 0) + 1
        return conteo
    except Exception:
        return {}


# ── ESTADO ───────────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history: List[Dict] = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files: List[str] = []


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.15em;"
        "text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem\">"
        "// Base de conocimiento</div>",
        unsafe_allow_html=True,
    )

    company_tone = st.selectbox(
        "Tono del asistente",
        ["Profesional y cercano", "Formal", "Claro y resolutivo"],
        index=0,
    )
    channel = st.selectbox("Canal", ["Chat Web", "Email", "WhatsApp"], index=0)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Sube PDFs de conocimiento",
        type=["pdf"],
        accept_multiple_files=True,
        help="Manuales de producto, FAQs, politicas de devolucion, terminos de servicio...",
    )

    if st.button("Indexar documentos", use_container_width=True):
        if uploaded_files:
            with st.spinner("Indexando..."):
                for f in uploaded_files:
                    count = index_pdf(f)
                    if f.name not in st.session_state.indexed_files:
                        st.session_state.indexed_files.append(f.name)
            st.success("Base de conocimiento lista.")
        else:
            st.warning("Sube archivos PDF primero.")

    if st.button("Borrar base y reiniciar", use_container_width=True):
        if Path(CHROMA_PATH).exists():
            shutil.rmtree(CHROMA_PATH)
        st.cache_resource.clear()
        st.session_state.chat_history = []
        st.session_state.indexed_files = []
        time.sleep(0.3)
        st.rerun()

    docs = get_docs_indexados()
    if docs:
        st.markdown(
            "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;"
            "text-transform:uppercase;color:#7a5e28;margin:1.25rem 0 .75rem\">"
            "// Documentos indexados</div>",
            unsafe_allow_html=True,
        )
        for nombre, n in docs.items():
            st.markdown(
                f"""<div class="doc-item">
                  <span class="doc-name">{nombre[:30]}{"..." if len(nombre) > 30 else ""}</span>
                  <span class="doc-chunks">{n} frags</span>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown(
        """
<div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;
    line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
    <span style="color:#4dd488">✓</span> Embeddings e indexado: local<br>
    <span style="color:#4dd488">✓</span> Base vectorial: ChromaDB en disco<br>
    <span style="color:#4dd488">✓</span> Respuesta: Groq con contexto recuperado<br>
    <span style="color:#d4a84b">!</span> Escala a humano si no hay respaldo documental
</div>
<div style="font-family:'DM Mono',monospace;font-size:.58rem;color:#44433f;margin-top:1.5rem">
    P07 · Chatbot atencion al cliente<br>
    <a href="https://github.com/chema74/portfolio-ia-aplicada/tree/main/portfolio/p07-chatbot-atencion-cliente"
       style="color:#7a5e28">Ver proyecto en GitHub</a>
</div>""",
        unsafe_allow_html=True,
    )


# ── CABECERA ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-tag">P07 · Chatbot atencion al cliente · Portfolio IA Aplicada
    <span class="groq-badge">✓ Groq · Llama 3.3 70B</span>
    <span class="local-badge">✓ ChromaDB local</span>
  </div>
  <div class="app-title">Chatbot de <em>atencion al cliente</em></div>
  <div class="app-subtitle">
    Carga la documentacion de tu empresa y el asistente responde basandose en ella.
    Escala automaticamente a persona cuando no tiene informacion suficiente.
  </div>
</div>""", unsafe_allow_html=True)

# ── ONBOARDING (sin documentos) ───────────────────────────────────────────────
docs_cargados = get_or_create_collection().count() > 0

if not docs_cargados:
    st.markdown("""
<div style="border:1px dashed rgba(212,168,75,.2);padding:3rem 2rem;text-align:center;margin-top:1rem">
  <div style="font-size:2.5rem;margin-bottom:1rem">💬</div>
  <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#8c8a84;margin-bottom:.75rem">
    Para empezar, sube los documentos de tu empresa
  </div>
  <div style="font-family:'DM Mono',monospace;font-size:.63rem;color:#44433f;letter-spacing:.06em;line-height:2">
    <b style="color:#d4a84b">Paso 1:</b> Ve al panel izquierdo y sube PDFs<br>
    <b style="color:#d4a84b">Paso 2:</b> Pulsa "Indexar documentos"<br>
    <b style="color:#d4a84b">Paso 3:</b> Escribe una pregunta en el cuadro de chat<br><br>
    Ejemplos de documentos utiles: manual de producto · FAQs · politica de devoluciones · terminos de servicio
  </div>
</div>""", unsafe_allow_html=True)
    st.stop()

# ── HISTORIAL DE CHAT ─────────────────────────────────────────────────────────
if st.session_state.chat_history:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;"
        "text-transform:uppercase;color:#7a5e28;margin-bottom:.75rem\">// Conversacion</div>",
        unsafe_allow_html=True,
    )

    for turn in st.session_state.chat_history:
        st.markdown(
            f'<div class="msg-user"><div class="msg-role">Tu</div>{turn["question"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="msg-bot"><div class="msg-role">Asistente</div>{turn["answer"]}</div>',
            unsafe_allow_html=True,
        )
        if turn.get("escalate"):
            st.markdown(
                '<div class="msg-escalate">'
                '⚠️ Esta consulta puede requerir atencion de una persona del equipo.'
                '</div>',
                unsafe_allow_html=True,
            )

    col_limpiar, _ = st.columns([1, 3])
    with col_limpiar:
        if st.button("Limpiar conversacion", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────────────────
col_q, col_btn = st.columns([5, 1])
with col_q:
    pregunta = st.text_input(
        "Escribe tu consulta",
        placeholder="Ej: Cual es el plazo de devolucion?  Como activo mi cuenta?",
        label_visibility="collapsed",
    )
with col_btn:
    enviar = st.button("Preguntar", use_container_width=True)

if enviar and pregunta.strip():
    try:
        get_groq_client()  # Valida la API key antes de continuar
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    with st.spinner("Consultando la base documental..."):
        answer, sources, escalate = generate_answer(
            pregunta.strip(),
            st.session_state.chat_history,
            company_tone,
            channel,
        )

    st.session_state.chat_history.append({
        "question": pregunta.strip(),
        "answer": answer,
        "sources": sources,
        "escalate": escalate,
    })
    st.rerun()

elif enviar and not pregunta.strip():
    st.warning("Escribe una pregunta antes de consultar.")


# ── FUENTES (TAB SEPARADO) ────────────────────────────────────────────────────
if st.session_state.chat_history:
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    with st.expander("Ver fragmentos consultados en la ultima respuesta"):
        last_sources = st.session_state.chat_history[-1].get("sources", [])
        if last_sources:
            for d, m in last_sources:
                st.markdown(
                    f'<div class="source-box">'
                    f'<span style="color:#d4a84b;font-family:\'DM Mono\',monospace;font-size:.6rem">'
                    f'{m["source"]}  ·  Pag. {m["page"]}</span><br>{d[:300]}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No se usaron fragmentos documentales en la ultima respuesta.")


st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='app-footer'>P07 · Chatbot atencion al cliente · "
    "Groq + ChromaDB local + sentence-transformers · "
    "Portfolio IA Aplicada · Jose Maria · Sevilla</div>",
    unsafe_allow_html=True,
)
