# products/nspa-psychological-orchestrator/app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="NSPA Psychological", layout="wide", page_icon="🧠")

st.title("🧠 NSPA Psychological Orchestrator")
st.caption("Salud mental • Soporte psicológico • Bienestar emocional • Safety-first")

with st.sidebar:
    st.header("👤 Nuevo Paciente")
    session_type = st.selectbox("Tipo", ["Evaluación inicial", "Seguimiento", "Crisis", "Cierre"])
    urgency_level = st.select_slider("Urgencia", options=["Baja", "Media", "Alta", "Crítica"])
    st.button("💚 Iniciar Sesión", type="primary")
    st.info("💡 Datos sintéticos para demo")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Pacientes Activos", "45", "+3")
col2.metric("Sesiones Esta Semana", "67", "+12")
col3.metric("Bienestar Promedio", "7.2/10", "+0.5")
col4.metric("Intervenciones Crisis", "2", "Esta semana")

# Pacientes
st.subheader("👥 Pacientes Activos")
patients_df = pd.DataFrame([
    {"ID": "PAT-001", "Nombre": "Paciente A", "Última Sesión": "2026-05-12", "Bienestar": "7.5/10", "Estado": "Estable", "Próxima": "2026-05-19"},
    {"ID": "PAT-002", "Nombre": "Paciente B", "Última Sesión": "2026-05-11", "Bienestar": "5.2/10", "Estado": "Seguimiento", "Próxima": "2026-05-14"},
    {"ID": "PAT-003", "Nombre": "Paciente C", "Última Sesión": "2026-05-10", "Bienestar": "8.1/10", "Estado": "Progreso", "Próxima": "2026-05-24"},
])
st.dataframe(patients_df, use_container_width=True, hide_index=True)

# Gráfico
st.subheader("📈 Evolución de Bienestar Promedio")
wellness_df = pd.DataFrame({
    "Semana": ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
    "Bienestar": [6.5, 6.8, 7.0, 7.2]
}).set_index("Semana")
st.line_chart(wellness_df, use_container_width=True)

# Alertas
st.subheader("⚠️ Alertas de Bienestar")
st.warning("🟡 Paciente B: Bienestar 5.2/10 - Requiere seguimiento cercano esta semana")
st.info("🔵 3 pacientes completaron terapia exitosamente este mes")
st.success("✅ Bienestar promedio mejoró 0.5 puntos este mes")

st.caption(f"Agentes_IA • NSPA Psychological • {datetime.now().strftime('%Y-%m-%d %H:%M')}")