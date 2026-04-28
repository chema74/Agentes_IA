"""
P09  Consultor RAG de Normativa de Comercio Internacional
===========================================================
Autor : Jos Mara
Stack : Groq  ChromaDB  sentence-transformers  PyMuPDF  Streamlit
Coste : GRATUITO
"""

import os, shutil
from pathlib import Path
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import fitz
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = str(BASE_DIR / "chroma_db_p08")
COLLECTION  = "normativa_comercio"
CHUNK_SIZE  = 700
CHUNK_OVERLAP = 120
TOP_K = 5

st.set_page_config(page_title="Consultor Normativa Comercio IA", page_icon="", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
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
.fuente-box{background:#0a0a0f;border:1px solid rgba(212,168,75,.1);padding:.75rem 1rem;margin-bottom:.4rem;font-size:.78rem;color:#8c8a84}
.custom-divider{height:1px;background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent);margin:1.5rem 0}
.app-footer{font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;text-align:center;padding-top:2rem}
[data-testid="stSidebar"]{background:#10101a !important;border-right:1px solid rgba(212,168,75,.12) !important}
</style>""", unsafe_allow_html=True)

@st.cache_resource
def get_groq():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_chroma():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name=COLLECTION, embedding_function=ef, metadata={"hnsw:space":"cosine"}) # type: ignore

def extraer_chunks(bytes_pdf, nombre):
    doc = fitz.open(stream=bytes_pdf, filetype="pdf")
    chunks = []
    for num_pag, pag in enumerate(doc, 1): # type: ignore
        texto = pag.get_text("text").strip()
        if not texto: continue
        inicio = 0
        while inicio < len(texto):
            chunk = texto[inicio:inicio+CHUNK_SIZE].strip()
            if len(chunk) > 50:
                chunks.append({"texto":chunk,"fuente":nombre,"pagina":num_pag,"id":f"{nombre}_p{num_pag}_c{inicio}"})
            inicio += CHUNK_SIZE - CHUNK_OVERLAP
    doc.close()
    return chunks

def indexar(collection, chunks, nombre):
    try:
        ids = collection.get(where={"fuente":nombre})["ids"]
        if ids: collection.delete(ids=ids)
    except: pass
    if chunks:
        collection.upsert(
            documents=[c["texto"] for c in chunks],
            ids=[c["id"] for c in chunks],
            metadatas=[{"fuente":c["fuente"],"pagina":c["pagina"]} for c in chunks],
        )

def buscar(collection, pregunta, k=TOP_K):
    if collection.count() == 0: return []
    r = collection.query(query_texts=[pregunta], n_results=min(k,collection.count()), include=["documents","metadatas","distances"])
    chunks = []
    if r and r["documents"]:
        for doc,meta,dist in zip(r["documents"][0],r["metadatas"][0],r["distances"][0]):
            chunks.append({"texto":doc,"fuente":meta.get("fuente",""),"pagina":meta.get("pagina",""),"score":round(1-dist,3)})
    return chunks

def responder(groq_client, pregunta, contexto, historial, pais_origen, pais_destino, producto):
    ctx_str = "\n\n---\n\n".join([f"[{c['fuente']}, Pg.{c['pagina']}]\n{c['texto']}" for c in contexto])
    ctx_empresa = ""
    if pais_origen or pais_destino or producto:
        ctx_empresa = f"\nCONTEXTO: Empresa de {pais_origen or 'Espaa'} exportando {producto or 'producto'} a {pais_destino or 'mercado destino'}."
    system = (
        f"Eres un experto en normativa de comercio internacional y comercio exterior.{ctx_empresa} "
        f"Responde EXCLUSIVAMENTE basndote en los documentos de normativa cargados. "
        f"Cita siempre el documento y pgina. Indica si la normativa puede estar desactualizada. "
        f"Si no encuentras la informacin, dilo claramente. Responde en espaol."
    )
    msgs = [{"role":"system","content":system}]
    for m in historial[-4:]: msgs.append({"role":m["role"],"content":m["content"]})
    msgs.append({"role":"user","content":f"NORMATIVA DISPONIBLE:\n{ctx_str}\n\nPREGUNTA: {pregunta}"})
    r = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, temperature=0.1, max_tokens=900)
    return r.choices[0].message.content

if "historial_p09" not in st.session_state: st.session_state.historial_p09 = []
if "docs_p09" not in st.session_state: st.session_state.docs_p09 = set()

PREGUNTAS_RAPIDAS = [
    "Qu aranceles aplican a este producto?",
    "Qu documentacin aduanera necesito?",
    "Cules son los requisitos de origen del producto?",
    "Qu acuerdos comerciales son aplicables?",
    "Existen barreras no arancelarias para este mercado?",
    "Qu certificaciones o homologaciones se requieren?",
]

with st.sidebar:
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem">// Cargar normativa</div>', unsafe_allow_html=True)
    archivos = st.file_uploader("Sube PDFs de normativa", type=["pdf"], accept_multiple_files=True,
        help="Guas ICEX, normativa OMC, acuerdos comerciales UE, reglamentos aduaneros...")

    if archivos:
        col = get_chroma()
        for arch in archivos:
            if arch.name not in st.session_state.docs_p09:
                with st.spinner(f"Indexando {arch.name}..."):
                    chunks = extraer_chunks(arch.read(), arch.name)
                    indexar(col, chunks, arch.name)
                    st.session_state.docs_p09.add(arch.name)
                st.success(f" {arch.name}")

    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-top:1rem;margin-bottom:.75rem">// Contexto de exportacin</div>', unsafe_allow_html=True)
    pais_origen  = st.text_input("Pas de origen", value="Espaa")
    pais_destino = st.text_input("Pas de destino", placeholder="Ej: Marruecos")
    producto     = st.text_input("Producto", placeholder="Ej: Aceite de oliva")

    if st.button("Borrar normativa", use_container_width=True):
        st.cache_resource.clear()
        import time; time.sleep(0.3)
        shutil.rmtree(CHROMA_PATH, ignore_errors=True)
        st.session_state.docs_p09 = set()
        st.session_state.historial_p09 = []
        st.rerun()

    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
    Fuentes recomendadas:<br>
    <span style="color:#7a5e28"> Guas de mercado ICEX</span><br>
    <span style="color:#7a5e28"> Acuerdos UE (EUR-Lex)</span><br>
    <span style="color:#7a5e28"> Reglamentos aduaneros</span></div>""", unsafe_allow_html=True)

st.markdown("""<div class="app-header">
  <div class="app-tag">P09  Normativa comercio  Portfolio IA Aplicada
    <span class="groq-badge"> Groq  ChromaDB local</span></div>
  <div class="app-title">Consultor de <em>Normativa</em></div>
  <div class="app-subtitle">Pregunta sobre aranceles, acuerdos comerciales, aduanas y requisitos de exportacin</div>
</div>""", unsafe_allow_html=True)

try:
    col = get_chroma()
    total = col.count()
except: total = 0

if total == 0:
    st.markdown("""<div style="border:1px dashed rgba(212,168,75,.2);padding:3rem;text-align:center">
    <div style="font-size:2.5rem;margin-bottom:1rem"></div>
    <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:#8c8a84;margin-bottom:.5rem">Carga documentos de normativa comercial</div>
    <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;line-height:1.9">
    Guas de mercado ICEX  Acuerdos comerciales UE  Reglamentos aduaneros<br>
    El asistente responder solo con lo que est en los documentos cargados</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem">Consultas frecuentes</div>', unsafe_allow_html=True)
st.markdown("".join([f'<span style="font-family:\'DM Mono\',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.15);color:#8c8a84;margin:.2rem;display:inline-block">{p}</span>' for p in PREGUNTAS_RAPIDAS]), unsafe_allow_html=True)
st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

for msg in st.session_state.historial_p09:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user"><div class="msg-role">T</div>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot"><div class="msg-role"> Consultor normativa</div>{msg["content"]}</div>', unsafe_allow_html=True)

if st.session_state.historial_p09:
    if st.button("Limpiar conversacin"): st.session_state.historial_p09 = []; st.rerun()
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

col_q, col_btn = st.columns([5,1])
with col_q:
    pregunta = st.text_input("Tu consulta de normativa", placeholder="Ej: Qu documentacin necesito para exportar aceite de oliva a Marruecos?", label_visibility="collapsed")
with col_btn:
    enviar = st.button("Consultar ", use_container_width=True)

if enviar and pregunta.strip():
    col = get_chroma()
    contexto = buscar(col, pregunta.strip())
    if not contexto:
        st.warning("No se encontr informacin relevante en la normativa cargada.")
    else:
        with st.spinner(" Consultando normativa..."):
            respuesta = responder(get_groq(), pregunta.strip(), contexto, st.session_state.historial_p09, pais_origen, pais_destino, producto)
        st.session_state.historial_p09.append({"role":"user","content":pregunta.strip()})
        st.session_state.historial_p09.append({"role":"assistant","content":respuesta})
        with st.expander(" Ver fragmentos de normativa consultados"):
            for c in contexto:
                st.markdown(f'<div class="fuente-box"><span style="color:#d4a84b;font-family:\'DM Mono\',monospace;font-size:.6rem">{c["fuente"]}  Pg.{c["pagina"]}  {c["score"]:.0%}</span><br>{c["texto"][:250]}</div>', unsafe_allow_html=True)
        st.rerun()

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="app-footer">P09  Consultor Normativa Comercio  Groq + ChromaDB  Portfolio IA Aplicada  Jos Mara  Sevilla</div>', unsafe_allow_html=True)
