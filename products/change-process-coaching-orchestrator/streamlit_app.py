from __future__ import annotations

import requests
import streamlit as st

API_BASE_URL_DEFAULT = "http://127.0.0.1:8060/api"
API_KEY_DEFAULT = "change-dev-key"

st.set_page_config(
    page_title="Change Process Coaching",
    page_icon="",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(16,24,40,1) 0%, rgba(10,14,22,1) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }

    .section-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1rem 1rem 0.8rem 1rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1rem;
        min-height: 110px;
    }

    .small-label {
        color: #9aa4b2;
        font-size: 0.82rem;
        margin-bottom: 0.25rem;
        letter-spacing: 0.02em;
    }

    .big-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }

    .muted-text {
        color: #aab3c0;
        font-size: 0.92rem;
    }

    .pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.04);
        font-size: 0.85rem;
        margin-right: 0.45rem;
        margin-bottom: 0.45rem;
    }

    .result-box {
        background: rgba(255,255,255,0.02);
        border-left: 4px solid #4c8bf5;
        border-radius: 12px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div style="font-size:0.95rem; color:#98a2b3; margin-bottom:0.35rem;">
            Demo operativa  evaluacion e intervencion en procesos de cambio
        </div>
        <div style="font-size:2.35rem; font-weight:800; line-height:1.05; margin-bottom:0.55rem;">
             Change Process Coaching Orchestrator
        </div>
        <div class="muted-text">
            Analiza tensiones, fatiga, bloqueos, ambiguedad y friccion organizativa.
            Devuelve una lectura estructurada del caso, una recomendacion y un plan de intervencion accionable.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Configuracion")
    api_base_url = st.text_input("API Base URL", value=API_BASE_URL_DEFAULT)
    api_key = st.text_input("X-API-Key", value=API_KEY_DEFAULT, type="password")
    requested_mode = st.radio("Modo de trabajo", options=["evaluate", "intervene"], index=0)

    st.markdown("---")
    st.caption("Modo `evaluate`: analiza el caso.")
    st.caption("Modo `intervene`: analiza y persiste el caso.")

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Entrada del caso")

process_notes = st.text_area(
    "Describe la situacin",
    height=190,
    placeholder="Ejemplo: Existe ambiguedad sobre prioridades, el equipo esta cansado y ademas hay retrasos en decisiones clave.",
)

col1, col2, col3 = st.columns(3)

with col1:
    context_type = st.selectbox(
        "Contexto",
        options=["organizational", "team", "individual"],
        index=0,
    )

with col2:
    change_phase = st.selectbox(
        "Fase del cambio",
        options=["assessment", "adoption", "execution", "stabilization"],
        index=0,
    )

with col3:
    change_goal = st.text_input(
        "Objetivo del cambio",
        value="Recuperar claridad y continuidad del proceso",
    )

sample_col1, sample_col2, sample_col3 = st.columns(3)

with sample_col1:
    if st.button("Caso ejemplo  conflicto", use_container_width=True):
        process_notes = "Hay tension entre responsables y conflicto abierto en reuniones clave."
        change_goal = "Recuperar alineamiento"
        st.session_state["sample_loaded"] = {
            "process_notes": process_notes,
            "change_goal": change_goal,
        }

with sample_col2:
    if st.button("Caso ejemplo  fatiga", use_container_width=True):
        process_notes = "El equipo est agotado, saturado y cansado del cambio."
        change_goal = "Reducir fatiga"
        st.session_state["sample_loaded"] = {
            "process_notes": process_notes,
            "change_goal": change_goal,
        }

with sample_col3:
    if st.button("Caso ejemplo  bloqueo", use_container_width=True):
        process_notes = "Hay retrasos, bloqueos operativos y dependencias que impiden avanzar."
        change_goal = "Recuperar ejecucion"
        st.session_state["sample_loaded"] = {
            "process_notes": process_notes,
            "change_goal": change_goal,
        }

if "sample_loaded" in st.session_state:
    sample = st.session_state["sample_loaded"]
    process_notes = st.text_area(
        "Notas del proceso cargadas",
        value=sample["process_notes"],
        height=190,
        key="loaded_notes",
    )
    change_goal = st.text_input(
        "Objetivo del cambio cargado",
        value=sample["change_goal"],
        key="loaded_goal",
    )

run = st.button("Analizar caso", type="primary", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if run:
    if not process_notes.strip():
        st.warning("Escribe primero unas notas del proceso.")
    else:
        payload = {
            "process_notes": process_notes,
            "context_type": context_type,
            "change_goal": change_goal,
            "change_phase": change_phase,
            "requested_mode": requested_mode,
            "case_id": None,
            "signals": [],
            "stakeholders": [],
            "sessions": [],
            "tasks": [],
            "survey_inputs": [],
            "source_systems": [],
        }

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        }

        endpoint = f"{api_base_url}/change-cases/{requested_mode}"

        try:
            with st.spinner("Procesando caso..."):
                response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
                response.raise_for_status()
                st.session_state.last_response = response.json()
            st.success("Caso procesado correctamente.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error llamando a la API: {e}")

data = st.session_state.last_response

def safe_get(obj: dict, *keys, default="-"):
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current not in [None, ""] else default

if data:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Resumen ejecutivo")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-label">Estado del proceso</div>
                <div class="big-value">{safe_get(data, "estado_del_proceso_de_cambio")}</div>
                <div class="muted-text">Lectura global del estado actual del caso.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-label">Nivel de friccion</div>
                <div class="big-value">{safe_get(data, "nivel_de_friccion", "level")}</div>
                <div class="muted-text">Intensidad estimada del desgaste del proceso.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-label">Fatiga</div>
                <div class="big-value">{safe_get(data, "alerta_de_fatiga_de_cambio", "level")}</div>
                <div class="muted-text">Senal de saturacion o sobrecarga detectada.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-label">Revision humana</div>
                <div class="big-value">{data.get("revision_humana_requerida", False)}</div>
                <div class="muted-text">Indica si el caso exige supervision humana explicita.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Recomendacion final")
    recomendacion = data.get("recomendacion_final", {})

    st.markdown(
        f"""
        <div class="result-box">
            <strong>Resumen:</strong> {recomendacion.get("summary", "-")}<br>
            <strong>Nivel:</strong> {recomendacion.get("level", "-")}<br>
            <strong>Justificacion:</strong> {recomendacion.get("rationale", "-")}<br>
            <strong>Siguiente responsable:</strong> {recomendacion.get("next_best_owner", "-")}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Plan de intervencion")
    plan = data.get("plan_de_intervencion", {})

    top1, top2, top3 = st.columns(3)
    top1.markdown(f"**Focus:** {plan.get('focus', '-')}")
    top2.markdown(f"**Modo:** {plan.get('intervention_mode', '-')}")
    top3.markdown(f"**Secuencia:** {plan.get('sequencing_rationale', '-')}")

    for idx, step in enumerate(plan.get("steps", []), start=1):
        title = f"Paso {idx}  {step.get('intervention_type', 'step')}"
        with st.expander(title, expanded=(idx == 1)):
            st.write(f"**Accion:** {step.get('step', '-')}")
            st.write(f"**Responsable:** {step.get('owner', '-')}")
            st.write(f"**Momento:** {step.get('timing', '-')}")
            st.write(f"**Objetivo:** {step.get('objective', '-')}")
            st.write(f"**Metrica de exito:** {step.get('success_metric', '-')}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Senales detectadas")
    signals = data.get("resumen_de_senales_detectadas", [])
    if signals:
        for signal in signals:
            with st.expander(f"{signal.get('category', '-')}  {signal.get('intensity', '-')}"):
                st.write(f"**Resumen:** {signal.get('summary', '-')}")
                st.write(f"**Fuente:** {signal.get('source', '-')}")
                st.write(f"**Confianza:** {signal.get('confidence', '-')}")
                st.write(f"**Extracto:** {signal.get('evidence_excerpt', '-')}")
    else:
        st.info("No hay senales detectadas para este caso.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Stakeholders y contexto")
    stakeholders = data.get("mapa_de_stakeholders_o_contexto_personal", [])
    if stakeholders:
        for item in stakeholders:
            with st.expander(f"{item.get('actor', '-')}  {item.get('role', '-')}"):
                st.write(f"**Influencia:** {item.get('influence', '-')}")
                st.write(f"**Alineamiento:** {item.get('alignment', '-')}")
                st.write(f"**Resistencia:** {item.get('resistance_level', '-')}")
                st.write(f"**Readiness:** {item.get('readiness_level', '-')}")
                st.write(f"**Apoyo necesario:** {item.get('support_needed', '-')}")
                st.write(f"**Notas:** {item.get('notes', '-')}")
    else:
        st.info("No hay stakeholders/contexto detallado para este caso.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Traizabilidad")
    st.code(
        f"case_id: {data.get('case_id', '-')}\nreferencia_de_auditoria: {data.get('referencia_de_auditoría', '-')}",
        language="text",
    )

    with st.expander("Ver JSON completo"):
        st.json(data)
    st.markdown("</div>", unsafe_allow_html=True)
