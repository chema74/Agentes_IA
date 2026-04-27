"""
P02 · ASISTENTE EJECUTIVO IA (VERSIÓN INDUSTRIAL CORREGIDA VISUALMENTE)
====================================================================
Autor : José María · Sevilla 2026
Lógica: Modular (Settings, Retry, RAG, Exporters, History, i18n, Validators)
UI : Corregida para Alta Legibilidad en Fondo Oscuro
"""

import json
import streamlit as st
from groq import Groq
from tavily import TavilyClient

# Importación de módulos propios (Pasos 1-9)
from config.settings import (
    GROQ_API_KEY, TAVILY_API_KEY, MODEL_NAME, 
    TEMPERATURE, MAX_TOKENS, MAX_RESULTS_PER_QUERY
)
from infrastructure.retry import with_retry
from domain.document_processor import extraer_texto_pdf, fragmentar_texto, buscar_contexto_relevante
from domain.logger import registrar_evento
from domain.exporters import exportar_a_word
from domain.history import (
    generar_id_sesion, guardar_sesion, cargar_sesion, listar_sesiones_disponibles
)
from domain.i18n import get_text
from domain.validators import sanitizar_peticion, validar_pdf_subido

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Executive AI", page_icon="🤖", layout="wide")

# Estilos Premium - CORREGIDOS PARA ALTA LEGIBILIDAD
# -> Forzamos contraste blanco en textos de chat y inputs
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,300&family=DM+Sans:wght@300;400;500&display=swap');
    
    /* Fondo base ultra-oscuro */
    html, body, [class*="css"] { 
        font-family: 'DM Sans', sans-serif; 
        background: #0c0c10; 
        color: #e4e2dc; /* Texto base claro, pero será sobreescrito en chat */
    }
    .stApp { background: #0c0c10; }
    
    /* Título de la aplicación */
    .app-title { 
        font-family: 'Fraunces', serif; 
        font-size: 2.5rem; 
        font-weight: 900; 
        color: #e4e2dc; /* Título claro */
    }
    .app-title em { color: #d4a84b; font-style: italic; font-weight: 300; }
    
    /* Contenedores de chat */
    .stChatMessage { 
        border-radius: 8px !important; 
        border: 1px solid rgba(212,168,75,0.1) !important; 
    }
    
    /* -------------------------------------------------------------------------
       CORRECCIÓN CRÍTICA DE LEGIBILIDAD
       Forzamos color blanco (#ffffff !important) en todos los elementos 
       de texto dentro de los mensajes de chat y el input del usuario.
       Esto soluciona el problema de texto oscuro sobre fondo oscuro.
       ------------------------------------------------------------------------- */
    .stChatMessage p, .stChatMessage div, .stChatInputContainer textarea {
        color: #ffffff !important; /* Blanco puro para máximo contraste */
    }
    
    /* Aseguramos que el avatar también se vea bien (opcional, pero ayuda) */
    .stChatMessage [data-testid="chatAvatarIcon"] {
        color: #d4a84b; /* Color acento dorado */
    }
</style>""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if "lang" not in st.session_state: st.session_state.lang = "es"
if "mensajes" not in st.session_state: st.session_state.mensajes = []
if "id_sesion" not in st.session_state: st.session_state.id_sesion = generar_id_sesion()
if "chunks_pdf" not in st.session_state: st.session_state.chunks_pdf = []
if "nombre_pdf" not in st.session_state: st.session_state.nombre_pdf = ""

# Clientes de API
groq_c = Groq(api_key=GROQ_API_KEY)
tavily_c = TavilyClient(api_key=TAVILY_API_KEY)

# --- SIDEBAR (HISTORIAL E IDIOMA) ---
with st.sidebar:
    st.session_state.lang = st.selectbox("🌐 Language", ["es", "en"], index=0)
    L = st.session_state.lang
    
    st.markdown(f"### {get_text('sidebar_history', lang=L)}")
    sesiones = listar_sesiones_disponibles()
    if sesiones:
        opciones = {s["id"]: s["label"] for s in sesiones}
        seleccion = st.selectbox("Cargar sesión", options=list(opciones.keys()), format_func=lambda x: opciones[x])
        if st.button("Cargar Seleccionada"):
            data = cargar_sesion(seleccion)
            if data:
                st.session_state.mensajes = data["chat"]
                st.session_state.id_sesion = data["metadata"]["id"]
                st.session_state.nombre_pdf = data["metadata"]["nombre_pdf"]
                st.rerun()

    st.markdown("---")
    pdf_file = st.file_uploader("Upload PDF", type="pdf")
    if pdf_file:
        errs = validar_pdf_subido(pdf_file.name, pdf_file.size)
        if not errs:
            texto = extraer_texto_pdf(pdf_file.read())
            st.session_state.chunks_pdf = fragmentar_texto(texto)
            st.session_state.nombre_pdf = pdf_file.name
            st.success(f"✅ {pdf_file.name}")
        else:
            for e in errs: st.error(e)

    if st.button(get_text("btn_new_chat", lang=L)):
        st.session_state.mensajes = []
        st.session_state.id_sesion = generar_id_sesion()
        st.session_state.nombre_pdf = ""
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.markdown(f'<div class="app-title">{get_text("title", lang=L)} <em>Pro</em></div>', unsafe_allow_html=True)
st.markdown(f'<p style="color:#8c8a84">{get_text("subtitle", lang=L)}</p>', unsafe_allow_html=True)

# Mostrar Historial
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- BUCLE DE RESPUESTA DEL AGENTE ---
if prompt := st.chat_input(get_text("input_placeholder", lang=L)):
    prompt_limpio, errs_v = sanitizar_peticion(prompt)
    if errs_v:
        for e in errs_v: st.error(e)
    else:
        st.session_state.mensajes.append({"role": "user", "content": prompt_limpio})
        with st.chat_message("user"): st.markdown(prompt_limpio)

        with st.chat_message("assistant", avatar="🤖"):
            with st.status(get_text("loading_tools", lang=L)) as status:
                
                # Definición de herramientas para el Tool Calling
                tools = [
                    {"type": "function", "function": {"name": "buscar_web", "parameters": {"type": "object", "properties": {"q": {"type": "string"}}}}},
                    {"type": "function", "function": {"name": "analizar_pdf", "parameters": {"type": "object", "properties": {"q": {"type": "string"}}}}}
                ]

                # Primera llamada: Descubrimiento de herramientas
                def call_groq_tools():
                    return groq_c.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role":"system","content":"Responde siempre en " + L}] + st.session_state.mensajes[-5:],
                        tools=tools, tool_choice="auto"
                    )
                
                res1 = with_retry(call_groq_tools, label="Tool Discovery")
                msg = res1.choices[0].message
                tool_results = []

                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        f_name = tc.function.name
                        f_args = json.loads(tc.function.arguments)
                        st.write(f"🔧 {f_name}...")
                        
                        if f_name == "buscar_web":
                            s = tavily_c.search(query=f_args.get("q"), max_results=MAX_RESULTS_PER_QUERY)
                            content = "\n".join([r["content"] for r in s["results"]])
                        elif f_name == "analizar_pdf":
                            content = buscar_contexto_relevante(f_args.get("q"), st.session_state.chunks_pdf)
                        
                        tool_results.append({"role":"tool", "tool_call_id": tc.id, "content": content})
                        registrar_evento("uso_herramienta", {"herramienta": f_name})
                    
                    status.update(label=get_text("status_done", lang=L), state="complete", expanded=False)

            # Respuesta Final con Streaming
            full_response = ""
            placeholder = st.empty()
            
            def call_groq_final():
                final_msgs = [{"role":"system","content":"Sintetiza la información de forma ejecutiva y profesional."}] + st.session_state.mensajes[-5:]
                if tool_results:
                    final_msgs.append(msg)
                    final_msgs.extend(tool_results)
                return groq_c.chat.completions.create(model=MODEL_NAME, messages=final_msgs, stream=True)

            stream = with_retry(call_groq_final, label="Final Answer")
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.mensajes.append({"role": "assistant", "content": full_response})
            
            # Guardado automático en Historial
            guardar_sesion(st.session_state.id_sesion, st.session_state.mensajes, st.session_state.nombre_pdf)

# --- ACCIONES FINALES ---
if st.session_state.mensajes:
    st.markdown("---")
    if st.button(get_text("btn_download", lang=L)):
        path_docx = exportar_a_word(st.session_state.mensajes, st.session_state.nombre_pdf)
        with open(path_docx, "rb") as f:
            st.download_button(get_text("btn_download", lang=L), f, file_name=path_docx.name)