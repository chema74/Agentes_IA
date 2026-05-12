# products/apollo-policy-enforcer-agent/app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Apollo Policy", layout="wide", page_icon="📋")

st.title("📋 Apollo Policy Enforcer Agent")
st.caption("Aplicación de políticas • Gobernanza • Enforcement automático • Policy-as-code")

with st.sidebar:
    st.header("⚙️ Configuración")
    policy_filter = st.selectbox("Filtrar Política", ["Todas", "Data Retention", "Access Control", "AI Ethics", "Backup"])
    enforcement_mode = st.selectbox("Modo", ["Audit", "Enforce", "Block"])
    st.info("💡 Datos sintéticos para demo")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Políticas Activas", "15", "+2")
col2.metric("Violaciones Bloqueadas", "3", "Esta semana")
col3.metric("Excepciones Aprobadas", "2", "Pendientes")
col4.metric("Revisiones Pendientes", "1", "⚠️")

# Políticas
st.subheader("📜 Políticas de Gobernanza")
policies_df = pd.DataFrame([
    {"ID": "POL-001", "Nombre": "Data Retention", "Estado": "Activa", "Última Ejecución": "2026-05-12", "Impacto": "Bajo", "Violaciones": "0"},
    {"ID": "POL-005", "Nombre": "Access Control", "Estado": "Violación", "Última Ejecución": "2026-05-12", "Impacto": "Alto", "Violaciones": "3"},
    {"ID": "POL-012", "Nombre": "AI Ethics", "Estado": "Revisión", "Última Ejecución": "2026-05-11", "Impacto": "Medio", "Violaciones": "1"},
    {"ID": "POL-008", "Nombre": "Backup", "Estado": "Activa", "Última Ejecución": "2026-05-12", "Impacto": "Bajo", "Violaciones": "0"},
])
st.dataframe(policies_df, use_container_width=True, hide_index=True)

# Gráfico
st.subheader("📊 Distribución de Violaciones por Política")
violations_df = pd.DataFrame({"Política": ["POL-001", "POL-005", "POL-012", "POL-008"], "Violaciones": [0, 3, 1, 0]}).set_index("Política")
st.bar_chart(violations_df, use_container_width=True)

# Alertas
st.subheader("⚠️ Alertas de Policy Enforcement")
st.error("🔴 Violación de política de control de acceso en endpoint /admin - Usuario: user_456")
st.warning("🟡 Política AI Ethics requiere actualización tras cambio regulatorio")
st.info("🔵 Excepción EXC-042 aprobada temporalmente hasta 2026-06-01")

st.caption(f"Agentes_IA • Apollo Policy • {datetime.now().strftime('%Y-%m-%d %H:%M')}")