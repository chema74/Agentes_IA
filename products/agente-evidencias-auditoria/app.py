# products/agente-evidencias-auditoria/app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Audit Compliance", layout="wide", page_icon="🔐")

st.title("🔐 Audit Compliance Evidence Agent")
st.caption("Auditoría automatizada • Evidencias de compliance • Trazabilidad • AI Act & RGPD")

with st.sidebar:
    st.header("🔍 Configuración de Auditoría")
    audit_scope = st.selectbox("Alcance", ["ISO 27001", "RGPD", "AI Act", "SOX", "Todos"])
    audit_date = st.date_input("Fecha Auditoría")
    st.button("🚀 Iniciar Auditoría", type="primary")
    st.info("💡 Datos sintéticos para demo")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Evidencias Generadas", "12", "+3")
col2.metric("Controles Validados", "8", "2 hoy")
col3.metric("Brechas Detectadas", "2", "⚠️")
col4.metric("Cumplimiento Promedio", "79.5%", "-2.3%")

# Evidencias
st.subheader("📋 Evidencias de Auditoría")
evidences_df = pd.DataFrame([
    {"ID": "EVD-001", "Control": "ISO 27001 A.9", "Tipo": "Acceso", "Estado": "Cumplido", "Fecha": "2026-05-10", "Riesgo": "Bajo"},
    {"ID": "EVD-002", "Control": "RGPD Art. 32", "Tipo": "Seguridad", "Estado": "Pendiente", "Fecha": "2026-05-12", "Riesgo": "Medio"},
    {"ID": "EVD-003", "Control": "AI Act Art. 15", "Tipo": "Transparencia", "Estado": "Crítico", "Fecha": "2026-05-11", "Riesgo": "Alto"},
    {"ID": "EVD-004", "Control": "SOX 404", "Tipo": "Financiero", "Estado": "Cumplido", "Fecha": "2026-05-09", "Riesgo": "Bajo"},
])
st.dataframe(evidences_df, use_container_width=True, hide_index=True)

# Gráfico de cumplimiento
st.subheader("📊 Nivel de Cumplimiento por Marco Normativo")
compliance_df = pd.DataFrame({
    "Marco": ["ISO 27001", "RGPD", "AI Act", "SOX 404"],
    "Cumplimiento %": [95, 78, 45, 100]
}).set_index("Marco")
st.bar_chart(compliance_df, use_container_width=True)

# Alertas
st.subheader("⚠️ Alertas de Compliance")
st.error("🔴 Brecha crítica en AI Act Art. 15 - Requiere acción inmediata")
st.warning("🟡 Control RGPD Art. 32 pendiente de validación técnica")
st.info("🔵 Próxima auditoría externa: 2026-06-15")

st.caption(f"Agentes_IA • Audit Compliance • {datetime.now().strftime('%Y-%m-%d %H:%M')}")