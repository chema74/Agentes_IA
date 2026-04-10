import os
import shutil
import time
from pathlib import Path
from typing import List, Tuple, Dict

import fitz  # PyMuPDF
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ==========================================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================================
load_dotenv()

st.set_page_config(
    page_title="P08 · Chatbot con Memoria",
    page_icon="💬",
    layout="wide",
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "atencion_cliente"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# ==========================================================
# 2. ESTILOS (CSS)
# ==========================================================
st.markdown("""
    <style>
        .main-title { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
        .subtitle { color: #666; margin-bottom: 1.5rem; }
        .info-box { padding: 1rem; border-radius: 0.5rem; background: #EBF5FF; border: 1px solid #BFDBFE; margin-bottom: 1rem; }
        .warning-box { padding: 1rem; border-radius: 0.5rem; background: #FFFBEB; border: 1px solid #FDE68A; margin-top: 1rem; }
        .success-box { padding: 1rem; border-radius: 0.5rem; background: #F0FDF4; border: 1px solid #BBF7D0; margin-top: 1rem; }
        .source-box { padding: 0.8rem; border-radius: 0.4rem; background: #F9FAFB; border: 1px solid #E5E7EB; margin-bottom: 0.5rem; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# 3. RECURSOS CACHEADOS
# ==========================================================
@st.cache_resource
def get_embedder():
    return SentenceTransformer(EMBED_MODEL_NAME)

@st.cache_resource
def get_chroma_client():
    return chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False),
    )

def get_or_create_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)

@st.cache_resource
def get_groq_client():
    return Groq(api_key=GROQ_API_KEY)

# ==========================================================
# 4. FUNCIONES DE PROCESAMIENTO
# ==========================================================
def extract_text_from_pdf(file) -> List[Tuple[int, str]]:
    pages = []
    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for i, page in enumerate(pdf): # type: ignore
            text = page.get_text("text").strip()
            if text:
                pages.append((i + 1, text))
        pdf.close()
    except Exception as e:
        st.error(f"Error leyendo PDF {file.name}: {e}")
    return pages

def split_text_smart(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Divide el texto buscando espacios para no romper palabras."""
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Intentar retroceder hasta el último espacio para no cortar palabras
            last_space = text.rfind(' ', start, end)
            if last_space != -1:
                end = last_space
        chunks.append(text[start:end].strip())
        start = end - overlap
    return chunks

def index_pdf(uploaded_file):
    collection = get_or_create_collection()
    embedder = get_embedder()
    pages = extract_text_from_pdf(uploaded_file)
    
    if not pages: return 0

    docs, ids, metadatas = [], [], []
    for page_num, page_text in pages:
        chunks = split_text_smart(page_text)
        for idx, chunk in enumerate(chunks):
            doc_id = f"{uploaded_file.name}_p{page_num}_c{idx}"
            docs.append(chunk)
            ids.append(doc_id)
            metadatas.append({"source": uploaded_file.name, "page": page_num})

    if docs:
        embeddings = embedder.encode(docs).tolist() # type: ignore
        collection.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)
    return len(docs)

# ==========================================================
# 5. LÓGICA DE RAG Y MEMORIA
# ==========================================================
def search_context(query: str, k: int = 4):
    collection = get_or_create_collection()
    embedder = get_embedder()
    query_embedding = embedder.encode([query]).tolist()[0] # type: ignore
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return list(zip(results["documents"][0], results["metadatas"][0])) # type: ignore

def generate_answer(question: str, history: List[Dict], tone: str, channel: str):
    context_items = search_context(question)
    context_text = "\n".join([f"[Doc: {m['source']} p.{m['page']}]: {d}" for d, m in context_items])
    
    # Construcción de la memoria (últimos 4 mensajes)
    memory_messages = []
    for turn in history[-4:]:
        memory_messages.append({"role": "user", "content": turn["question"]})
        memory_messages.append({"role": "assistant", "content": turn["answer"]})

    system_prompt = f"""Eres un experto en atención al cliente. Tono: {tone}. Canal: {channel}.
    REGLAS:
    1. Usa SOLO el contexto proporcionado. 
    2. Si no lo sabes, di que no tienes la información y sugiere hablar con un humano.
    3. RECUERDA la conversación previa si el usuario hace preguntas de seguimiento.
    4. Cita la "Base documental" al final.
    CONTEXTO:
    {context_text}"""

    messages = [{"role": "system", "content": system_prompt}] + memory_messages + [{"role": "user", "content": question}]

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages, # type: ignore
            temperature=0.2
        )
        answer = response.choices[0].message.content
        
        # Lógica de escalado
        low_conf = ["no tengo información", "no puedo confirmar", "agente humano", "no aparece"]
        escalate = any(word in answer.lower() for word in low_conf) or len(context_items) == 0 # type: ignore
        
        return answer, context_items, escalate
    except Exception as e:
        return f"Error en API: {e}", [], True

# ==========================================================
# 6. INTERFAZ STREAMLIT
# ==========================================================
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "indexed_files" not in st.session_state: st.session_state.indexed_files = []

st.markdown('<div class="main-title">💬 Chatbot Pro Atención al Cliente</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Inteligencia con memoria basada en tu propia documentación.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuración")
    company_tone = st.selectbox("Tono", ["Profesional y cercano", "Formal", "Claro y resolutivo"], index=0)
    channel = st.selectbox("Canal", ["Email", "Chat Web", "WhatsApp"], index=1)
    
    st.divider()
    uploaded_files = st.file_uploader("Subir base de conocimiento (PDF)", type=["pdf"], accept_multiple_files=True)
    
    if st.button("📥 Indexar Documentos", use_container_width=True):
        if uploaded_files:
            with st.spinner("Indexando..."):
                for f in uploaded_files:
                    count = index_pdf(f)
                    if f.name not in st.session_state.indexed_files:
                        st.session_state.indexed_files.append(f.name)
            st.success("¡Base de datos lista!")
        else:
            st.warning("Sube archivos primero.")

    if st.button("🧹 Borrar Base de Datos", use_container_width=True):
        if Path(CHROMA_PATH).exists():
            shutil.rmtree(CHROMA_PATH)
        st.session_state.chat_history = []
        st.session_state.indexed_files = []
        st.rerun()

    st.subheader("📚 Documentos")
    for f in st.session_state.indexed_files: st.caption(f"• {f}")

# Cuerpo Principal
tab1, tab2 = st.tabs(["💬 Chat", "📎 Evidencia"])

with tab1:
    # Contenedor para el historial de chat (estilo burbuja)
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            with st.chat_message("user"): st.write(chat["question"])
            with st.chat_message("assistant"): 
                st.write(chat["answer"])
                if chat["escalate"]:
                    st.warning("⚠️ Se recomienda derivar esta consulta a un humano.")

    # Input del usuario
    if prompt := st.chat_input("Escribe tu duda aquí..."):
        if not GROQ_API_KEY:
            st.error("Configura GROQ_API_KEY en el .env")
        else:
            with st.spinner("Consultando documentos..."):
                ans, docs, esc = generate_answer(prompt, st.session_state.chat_history, company_tone, channel) # type: ignore
                st.session_state.chat_history.append({
                    "question": prompt, "answer": ans, "sources": docs, "escalate": esc
                })
            st.rerun()

with tab2:
    if st.session_state.chat_history:
        last_sources = st.session_state.chat_history[-1]["sources"]
        if last_sources:
            for d, m in last_sources:
                st.markdown(f"""<div class="source-box"><b>Fuente: {m['source']} (Pág. {m['page']})</b><br>{d}</div>""", unsafe_allow_html=True)
        else:
            st.info("No se usaron documentos en la última respuesta.")
    else:
        st.info("Inicia un chat para ver la evidencia aquí.")