# products/agentic-learning-integrity-orchestrator/app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Learning Integrity", layout="wide", page_icon="📚")

st.title("📚 Agentic Learning Integrity Orchestrator")
st.caption("Integridad académica • Verificación de aprendizaje • Detección de plagio • Evaluación ética")

with st.sidebar:
    st.header("🔍 Verificación")
    student_id = st.text_input("ID Estudiante", "STU-2026-001")
    assessment_type = st.selectbox("Tipo", ["Examen", "Trabajo", "Proyecto", "Tesis"])
    st.button("🔎 Verificar Integridad", type="primary")
    st.info("💡 Datos sintéticos para demo")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Evaluaciones Procesadas", "156", "+12")
col2.metric("Integridad Verificada", "142", "91%")
col3.metric("Alertas Detectadas", "14", "⚠️")
col4.metric("Falsos Positivos", "3", "-20%")

# Evaluaciones
st.subheader("📊 Evaluaciones Recientes")
assessments_df = pd.DataFrame([
    {"ID": "ASM-001", "Estudiante": "STU-001", "Tipo": "Examen", "Integridad": "Verificada", "Confianza": "96%", "Fecha": "2026-05-12"},
    {"ID": "ASM-002", "Estudiante": "STU-002", "Tipo": "Trabajo", "Integridad": "Alerta", "Confianza": "68%", "Fecha": "2026-05-12"},
    {"ID": "ASM-003", "Estudiante": "STU-003", "Tipo": "Proyecto", "Integridad": "Verificada", "Confianza": "94%", "Fecha": "2026-05-11"},
    {"ID": "ASM-004", "Estudiante": "STU-004", "Tipo": "Tesis", "Integridad": "Revisión", "Confianza": "72%", "Fecha": "2026-05-11"},
])
st.dataframe(assessments_df, use_container_width=True, hide_index=True)

# Gráfico
st.subheader("📈 Tasa de Integridad por Tipo de Evaluación")
integrity_df = pd.DataFrame({"Tipo": ["Examen", "Trabajo", "Proyecto", "Tesis"], "Integridad %": [95, 88, 92, 85]}).set_index("Tipo")
st.bar_chart(integrity_df, use_container_width=True)

# Alertas
st.subheader("⚠️ Alertas de Integridad")
st.warning("🟡 Similitud del 45% detectada en trabajo ASM-002 - Requiere revisión manual")
st.info("🔵 Estudiante STU-004: Patrón de escritura inconsistente en tesis - Análisis lingüístico recomendado")
st.success("✅ 142 evaluaciones validadas sin incidencias esta semana")

st.caption(f"Agentes_IA • Learning Integrity • {datetime.now().strftime('%Y-%m-%d %H:%M')}")