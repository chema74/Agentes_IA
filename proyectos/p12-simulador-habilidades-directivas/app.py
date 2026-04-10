"""
P29 · Simulador de habilidades directivas
========================================
Autor: José María
Stack: Groq · Streamlit

Cómo funciona:
1. El usuario selecciona un escenario de liderazgo o gestión.
2. La IA interpreta a un interlocutor y abre la conversación.
3. El usuario responde como directivo.
4. La conversación avanza por turnos.
5. Al finalizar, la app genera un feedback orientativo para reflexión y práctica.
"""

import json
import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

CLAVES_FEEDBACK = {"puntuacion", "nivel", "fortalezas", "mejoras", "alternativa", "resumen"}

ESCENARIOS = {
    "Dar feedback negativo a un empleado con bajo rendimiento": {
        "rol_interlocutor": "empleado con bajo rendimiento que se pone a la defensiva",
        "contexto": "Llevas 3 meses viendo que el empleado no cumple sus objetivos. Ha habido avisos informales pero sin resultado. Hoy tienes la conversación formal.",
        "habilidad": "feedback constructivo",
    },
    "Gestionar un conflicto entre dos miembros del equipo": {
        "rol_interlocutor": "empleado que acusa a su compañero de no hacer su parte del trabajo",
        "contexto": "Dos miembros de tu equipo llevan semanas sin hablarse. El conflicto está afectando al rendimiento del grupo. Has citado a cada uno por separado.",
        "habilidad": "gestión de conflictos",
    },
    "Comunicar un cambio organizacional impopular": {
        "rol_interlocutor": "empleado veterano muy reacio al cambio que lleva 15 años en la empresa",
        "contexto": "La empresa ha decidido reorganizar departamentos. Algunos puestos cambian de función. Hay incertidumbre y rumores en el equipo.",
        "habilidad": "gestión del cambio",
    },
    "Motivar a un equipo desmotivado tras malos resultados": {
        "rol_interlocutor": "miembro del equipo escéptico que duda de que las cosas vayan a cambiar",
        "contexto": "El equipo acaba de cerrar un trimestre muy por debajo de objetivos. El ambiente es tenso y hay sensación de fracaso colectivo.",
        "habilidad": "liderazgo motivacional",
    },
    "Negociar con un colaborador que pide un aumento": {
        "rol_interlocutor": "empleado valioso que ha recibido una oferta de otra empresa y viene a negociar",
        "contexto": "Es un perfil clave del equipo. Su salario está en la media del mercado. El presupuesto de RR. HH. tiene limitaciones este año.",
        "habilidad": "negociación y retención de talento",
    },
    "Delegar una tarea importante a alguien que no confía en sí mismo": {
        "rol_interlocutor": "empleado competente pero con poca autoconfianza que pone obstáculos a asumir el encargo",
        "contexto": "Quieres dar más responsabilidad a este empleado. Es capaz, pero siempre dice que no está listo o que le falta experiencia.",
        "habilidad": "delegación y desarrollo de personas",
    },
}


st.set_page_config(
    page_title="Simulador de habilidades directivas",
    page_icon="🎭",
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
.block-container { padding-top:2rem; padding-bottom:2rem; max-width:950px; }
.app-tag { font-family:'DM Mono',monospace; font-size:.65rem; letter-spacing:.2em; text-transform:uppercase; color:#d4a84b; margin-bottom:.75rem; }
.app-title { font-family:'Fraunces',serif; font-size:2.2rem; font-weight:900; line-height:1.1; margin:0; }
.app-title em { font-style:italic; font-weight:300; color:#d4a84b; }
.app-subtitle { color:#8c8a84; font-size:.9rem; margin-top:.5rem; }
.app-header { border-bottom:1px solid rgba(212,168,75,.2); padding-bottom:1.5rem; margin-bottom:2rem; }
.groq-badge { display:inline-flex; align-items:center; gap:.4rem; font-family:'DM Mono',monospace; font-size:.6rem; color:#4dd488; border:1px solid rgba(77,212,136,.25); padding:.2rem .6rem; margin-left:.75rem; }
.stTextInput > label, .stTextArea > label, .stSelectbox > label { font-family:'DM Mono',monospace !important; font-size:.7rem !important; letter-spacing:.12em !important; text-transform:uppercase !important; color:#d4a84b !important; }
.stTextInput input, .stTextArea textarea { background:#14141c !important; border:1px solid rgba(212,168,75,.25) !important; border-radius:3px !important; color:#e4e2dc !important; }
[data-baseweb="select"] > div { background:#14141c !important; border:1px solid rgba(212,168,75,.25) !important; border-radius:3px !important; color:#e4e2dc !important; }
.stButton > button { background:#d4a84b !important; color:#0c0c10 !important; border:none !important; border-radius:3px !important; font-family:'DM Mono',monospace !important; font-size:.75rem !important; font-weight:700 !important; letter-spacing:.1em !important; text-transform:uppercase !important; padding:.65rem 2rem !important; }
.stButton > button:hover { background:#e8c97a !important; transform:translateY(-1px); }
.scenario-box { background:#14141c; border:1px solid rgba(212,168,75,.2); padding:1.5rem 2rem; margin-bottom:1.5rem; position:relative; }
.scenario-box::before { content:''; position:absolute; top:0;left:0; width:3px;height:100%; background:linear-gradient(180deg,#d4a84b,transparent); }
.scenario-label { font-family:'DM Mono',monospace; font-size:.62rem; letter-spacing:.12em; text-transform:uppercase; color:#7a5e28; margin-bottom:.5rem; }
.scenario-text { font-size:.95rem; line-height:1.8; color:#e4e2dc; }
.msg-interlocutor { background:#14141c; border:1px solid rgba(212,75,75,.15); border-left:3px solid #e87878; padding:1.1rem 1.4rem; margin-bottom:.6rem; font-size:.9rem; line-height:1.8; }
.msg-directivo { background:rgba(212,168,75,.06); border:1px solid rgba(212,168,75,.12); padding:1rem 1.25rem; margin-bottom:.5rem; font-size:.9rem; line-height:1.75; }
.msg-role { font-family:'DM Mono',monospace; font-size:.58rem; color:#44433f; letter-spacing:.1em; text-transform:uppercase; margin-bottom:.35rem; }
.feedback-box { background:rgba(77,212,136,.04); border:1px solid rgba(77,212,136,.2); padding:1.25rem 1.5rem; margin-top:1rem; }
.feedback-label { font-family:'DM Mono',monospace; font-size:.62rem; color:#4dd488; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.5rem; }
.score-badge { display:inline-flex; align-items:center; font-family:'DM Mono',monospace; font-size:.75rem; padding:.3rem .8rem; border-radius:2px; font-weight:700; }
.score-alto   { background:rgba(77,212,136,.1);  color:#4dd488; border:1px solid rgba(77,212,136,.3); }
.score-medio  { background:rgba(212,168,75,.1);  color:#d4a84b; border:1px solid rgba(212,168,75,.3); }
.score-bajo   { background:rgba(212,75,75,.1);   color:#e87878; border:1px solid rgba(212,75,75,.3); }
.aviso-box { background:rgba(212,168,75,.05); border:1px solid rgba(212,168,75,.18); padding:1rem 1.25rem; margin-bottom:1rem; font-size:.875rem; color:#d7d2c5; }
.custom-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent); margin:1.5rem 0; }
.app-footer { font-family:'DM Mono',monospace; font-size:.62rem; color:#44433f; text-align:center; padding-top:2rem; }
[data-testid="stSidebar"] { background:#10101a !important; border-right:1px solid rgba(212,168,75,.12) !important; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_groq() -> Groq:
    """Crea el cliente de Groq si la API key está disponible."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y añade tu clave antes de iniciar una simulación."
        )
    return Groq(api_key=api_key)


def extraer_json_objeto(texto: str) -> dict:
    """Extrae y valida el primer objeto JSON útil de la respuesta del modelo."""
    if not texto:
        raise ValueError("El modelo no devolvió contenido.")

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

    raise ValueError("La respuesta del modelo no contenía un JSON válido.")


def normalizar_feedback(data: dict) -> dict:
    """Valida la estructura mínima del feedback final."""
    faltantes = CLAVES_FEEDBACK - set(data.keys())
    if faltantes:
        raise ValueError(f"Faltan claves obligatorias en el feedback: {', '.join(sorted(faltantes))}.")

    try:
        puntuacion = float(data.get("puntuacion", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("La puntuación del feedback no es válida.") from exc

    feedback = {
        "puntuacion": max(0.0, min(10.0, round(puntuacion, 1))),
        "nivel": str(data.get("nivel", "Medio")).strip() or "Medio",
        "fortalezas": [str(x).strip() for x in data.get("fortalezas", []) if str(x).strip()],
        "mejoras": [str(x).strip() for x in data.get("mejoras", []) if str(x).strip()],
        "alternativa": str(data.get("alternativa", "")).strip(),
        "resumen": str(data.get("resumen", "")).strip(),
    }

    if not feedback["resumen"]:
        raise ValueError("El feedback no incluye un resumen utilizable.")

    return feedback


def generar_apertura(esc_data: dict, nivel_dificultad: str) -> str:
    """Genera la frase inicial del interlocutor."""
    dificultad_map = {
        "Colaborador": "algo colaborador, aunque con reservas",
        "Resistente": "resistente y a la defensiva",
        "Muy difícil": "muy difícil, evasivo o especialmente tenso",
    }
    actitud = dificultad_map.get(nivel_dificultad, "colaborador")
    system_interlocutor = (
        f"Eres {esc_data['rol_interlocutor']}. "
        f"Tu actitud es {actitud}. "
        f"Contexto: {esc_data['contexto']} "
        "Responde de forma realista y humana, sin exageración dramática. "
        "Máximo 3 frases. Responde en español."
    )
    respuesta = get_groq().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_interlocutor},
            {"role": "user", "content": "Empieza la conversación con una frase inicial realista para este escenario."},
        ],
        temperature=0.7,
        max_tokens=150,
    )
    contenido = respuesta.choices[0].message.content
    if not contenido:
        raise ValueError("El interlocutor no devolvió una apertura utilizable.")
    return contenido.strip()


def generar_respuesta_interlocutor(esc_data: dict, nivel_dificultad: str, conversacion: list, respuesta_directivo: str) -> str:
    """Genera la siguiente respuesta del interlocutor."""
    dificultad_map = {
        "Colaborador": "algo colaborador, aunque con reservas",
        "Resistente": "resistente y a la defensiva",
        "Muy difícil": "muy difícil, evasivo o especialmente tenso",
    }
    actitud = dificultad_map.get(nivel_dificultad, "colaborador")
    system_interlocutor = (
        f"Eres {esc_data['rol_interlocutor']}. Tu actitud es {actitud}. "
        f"Contexto: {esc_data['contexto']} "
        "Reacciona de forma realista a lo que acaba de decir el directivo. "
        "Máximo 3 frases. Responde en español. No seas exageradamente dramático."
    )
    mensajes = [{"role": "system", "content": system_interlocutor}]
    for mensaje in conversacion:
        rol = "assistant" if mensaje["role"] == "interlocutor" else "user"
        mensajes.append({"role": rol, "content": mensaje["content"]})
    mensajes.append({"role": "user", "content": respuesta_directivo.strip()})

    respuesta = get_groq().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=mensajes,
        temperature=0.7,
        max_tokens=150,
    )
    contenido = respuesta.choices[0].message.content
    if not contenido:
        raise ValueError("El interlocutor no devolvió una respuesta utilizable.")
    return contenido.strip()


def generar_feedback(esc_data: dict, conversacion: list) -> dict:
    """Genera un feedback orientativo posterior a la simulación."""
    conv_txt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in conversacion])
    prompt = (
        f"Analiza esta simulación de práctica directiva centrada en '{esc_data['habilidad']}'.\n\n"
        f"CONVERSACIÓN:\n{conv_txt}\n\n"
        "Genera un feedback orientativo en JSON con:\n"
        "puntuacion: número del 1 al 10 como señal orientativa de desempeño en esta simulación\n"
        "nivel: 'Alto', 'Medio' o 'Bajo'\n"
        "fortalezas: lista de 2-3 cosas que se hicieron bien\n"
        "mejoras: lista de 2-3 aspectos a mejorar\n"
        "alternativa: una formulación alternativa útil en el momento más delicado\n"
        "resumen: 2 frases de valoración general\n\n"
        "Importante: no presentes esto como evaluación objetiva de competencias ni como diagnóstico. Devuelve solo JSON válido, sin markdown."
    )
    respuesta = get_groq().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600,
    )
    contenido = respuesta.choices[0].message.content or ""
    data = extraer_json_objeto(contenido)
    return normalizar_feedback(data)


if "conversacion" not in st.session_state:
    st.session_state.conversacion = []
if "simulacion_activa" not in st.session_state:
    st.session_state.simulacion_activa = False
if "escenario_actual" not in st.session_state:
    st.session_state.escenario_actual = None
if "feedback_final" not in st.session_state:
    st.session_state.feedback_final = None

with st.sidebar:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem\">// Configurar simulación</div>",
        unsafe_allow_html=True,
    )
    escenario_sel = st.selectbox("Escenario", list(ESCENARIOS.keys()))
    nombre_directivo = st.text_input("Tu nombre (opcional)", placeholder="Ej: Carlos")
    nivel_dificultad = st.selectbox("Dificultad del interlocutor", ["Colaborador", "Resistente", "Muy difícil"])

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    if st.button("Iniciar simulación", use_container_width=True):
        st.session_state.conversacion = []
        st.session_state.feedback_final = None
        st.session_state.escenario_actual = escenario_sel
        st.session_state.simulacion_activa = True
        st.rerun()

    if st.session_state.simulacion_activa:
        st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
        if st.button("Terminar y ver feedback", use_container_width=True):
            st.session_state.simulacion_activa = False
            if st.session_state.conversacion:
                esc_actual = st.session_state.escenario_actual
                esc = ESCENARIOS.get(esc_actual, {}) if esc_actual else {}
                try:
                    st.session_state.feedback_final = generar_feedback(esc, st.session_state.conversacion)
                except Exception as exc:
                    st.session_state.feedback_final = {"error": str(exc) or "No se pudo generar el feedback orientativo."}
            st.rerun()

    st.markdown(
        """
    <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
        <span style="color:#4dd488">●</span> La IA interpreta al interlocutor<br>
        <span style="color:#4dd488">●</span> Feedback posterior orientativo<br>
        <span style="color:#d4a84b">●</span> Herramienta de práctica, no evaluación profesional
    </div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="app-header">
  <div class="app-tag">P29 · Simulador de habilidades directivas · Portfolio IA Aplicada
    <span class="groq-badge">⚡ Groq · Llama 3.3 70B</span>
  </div>
  <div class="app-title">Simulador de <em>habilidades directivas</em></div>
  <div class="app-subtitle">Practica conversaciones difíciles de liderazgo y gestión con un interlocutor simulado por IA.</div>
</div>""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="aviso-box">
<strong>Aviso importante:</strong> esta herramienta está pensada para práctica y reflexión. No sustituye formación, coaching ni evaluación profesional, y el feedback final debe interpretarse como orientativo.
</div>""",
    unsafe_allow_html=True,
)

if not st.session_state.simulacion_activa and not st.session_state.conversacion:
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;margin-bottom:1rem\">Escenarios disponibles</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, (escenario, data) in enumerate(ESCENARIOS.items()):
        with cols[i % 2]:
            st.markdown(
                f"""
            <div style="border:1px solid rgba(212,168,75,.12);background:#14141c;padding:1.25rem;margin-bottom:.75rem">
              <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#d4a84b;margin-bottom:.4rem">{data['habilidad'].upper()}</div>
              <div style="font-size:.85rem;color:#c8c6c0;line-height:1.6">{escenario}</div>
            </div>""",
                unsafe_allow_html=True,
            )
    st.markdown(
        """
    <div style="text-align:center;padding:1.5rem;color:#44433f;font-family:'DM Mono',monospace;font-size:.62rem">
        Selecciona un escenario y pulsa iniciar simulación.
    </div>""",
        unsafe_allow_html=True,
    )

elif st.session_state.simulacion_activa:
    esc_actual = st.session_state.escenario_actual
    if not esc_actual:
        st.error("No hay un escenario activo. Selecciona uno desde el panel lateral.")
        st.session_state.simulacion_activa = False
        st.rerun()

    esc_data = ESCENARIOS[esc_actual]
    nombre_d = nombre_directivo or "Directivo"

    st.markdown(
        f"""
    <div class="scenario-box">
      <div class="scenario-label">Escenario activo · {esc_data['habilidad']}</div>
      <div class="scenario-text">{esc_data['contexto']}</div>
      <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#7a5e28;margin-top:.75rem">
        Interlocutor: {esc_data['rol_interlocutor']} · Dificultad: {nivel_dificultad}
      </div>
    </div>""",
        unsafe_allow_html=True,
    )

    if not st.session_state.conversacion:
        with st.spinner("Preparando al interlocutor..."):
            try:
                apertura = generar_apertura(esc_data, nivel_dificultad)
                st.session_state.conversacion.append({"role": "interlocutor", "content": apertura})
                st.rerun()
            except Exception as exc:
                st.error(f"No se pudo iniciar la simulación: {exc}")
                st.session_state.simulacion_activa = False

    for mensaje in st.session_state.conversacion:
        if mensaje["role"] == "interlocutor":
            st.markdown(
                f'<div class="msg-interlocutor"><div class="msg-role">Interlocutor</div>{mensaje["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg-directivo"><div class="msg-role">{nombre_d}</div>{mensaje["content"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    col_q, col_btn = st.columns([5, 1])
    with col_q:
        respuesta_directivo = st.text_input(
            "Tu respuesta como directivo",
            placeholder="¿Qué le dices?",
            label_visibility="collapsed",
        )
    with col_btn:
        enviar = st.button("Responder →", use_container_width=True)

    if enviar and respuesta_directivo.strip():
        with st.spinner("El interlocutor está respondiendo..."):
            try:
                respuesta_interlocutor = generar_respuesta_interlocutor(
                    esc_data,
                    nivel_dificultad,
                    st.session_state.conversacion,
                    respuesta_directivo.strip(),
                )
            except Exception as exc:
                st.error(f"No se pudo generar la respuesta del interlocutor: {exc}")
                st.stop()

        st.session_state.conversacion.append({"role": "directivo", "content": respuesta_directivo.strip()})
        st.session_state.conversacion.append({"role": "interlocutor", "content": respuesta_interlocutor})
        st.rerun()

    elif enviar and not respuesta_directivo.strip():
        st.warning("Escribe una respuesta antes de continuar la simulación.")

if not st.session_state.simulacion_activa and st.session_state.feedback_final and st.session_state.conversacion:
    fb = st.session_state.feedback_final
    esc_actual = st.session_state.escenario_actual
    esc_data = ESCENARIOS.get(esc_actual, {}) if esc_actual else {}

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;margin-bottom:.75rem\">Replay de la simulación</div>",
        unsafe_allow_html=True,
    )
    for mensaje in st.session_state.conversacion:
        if mensaje["role"] == "interlocutor":
            st.markdown(
                f'<div class="msg-interlocutor"><div class="msg-role">Interlocutor</div>{mensaje["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg-directivo"><div class="msg-role">{nombre_directivo or "Directivo"}</div>{mensaje["content"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    if "error" not in fb:
        puntuacion = fb.get("puntuacion", 5)
        nivel_fb = fb.get("nivel", "Medio")
        score_css = {"Alto": "score-alto", "Medio": "score-medio", "Bajo": "score-bajo"}.get(nivel_fb, "score-medio")

        st.markdown(
            f"""
        <div class="feedback-box">
          <div class="feedback-label">Feedback orientativo · {esc_data.get('habilidad', '')}</div>
          <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.25rem">
            <span class="score-badge" style="font-size:1.5rem">{puntuacion}/10</span>
            <span class="score-badge {score_css}">{nivel_fb}</span>
          </div>
          <div style="font-size:.9rem;color:#c8c6c0;line-height:1.8;margin-bottom:1rem">{fb.get('resumen', '')}</div>
        </div>""",
            unsafe_allow_html=True,
        )

        col_f, col_m = st.columns(2)
        with col_f:
            st.markdown(
                "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;color:#4dd488;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.5rem\">Puntos fuertes observados</div>",
                unsafe_allow_html=True,
            )
            for fortaleza in fb.get("fortalezas", []):
                st.markdown(
                    f'<div style="padding:.4rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem">· {fortaleza}</div>',
                    unsafe_allow_html=True,
                )
        with col_m:
            st.markdown(
                "<div style=\"font-family:'DM Mono',monospace;font-size:.62rem;color:#e87878;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.5rem\">Aspectos a mejorar</div>",
                unsafe_allow_html=True,
            )
            for mejora in fb.get("mejoras", []):
                st.markdown(
                    f'<div style="padding:.4rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem">· {mejora}</div>',
                    unsafe_allow_html=True,
                )

        alternativa = fb.get("alternativa", "")
        if alternativa:
            st.markdown(
                f"""
            <div style="background:rgba(212,168,75,.06);border:1px solid rgba(212,168,75,.2);padding:1rem 1.25rem;margin-top:1rem">
              <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#7a5e28;margin-bottom:.4rem">Formulación alternativa posible</div>
              <div style="font-size:.875rem;font-style:italic;color:#e4e2dc">"{alternativa}"</div>
            </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.error(f"No se pudo generar el feedback orientativo: {fb.get('error', 'Desconocido')}")

    if st.button("Nueva simulación", use_container_width=False):
        st.session_state.conversacion = []
        st.session_state.feedback_final = None
        st.session_state.simulacion_activa = False
        st.rerun()

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="app-footer">P29 · Simulador de habilidades directivas · Groq · Portfolio IA Aplicada · José María · Sevilla</div>',
    unsafe_allow_html=True,
)
