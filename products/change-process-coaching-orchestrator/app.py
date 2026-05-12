# products/change-process-coaching-orchestrator/app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Change Coaching", layout="wide", page_icon="🎯")

st.title("🎯 Change Process Coaching Orchestrator")
st.caption("Gestión del cambio • Coaching organizacional • Adopción • Resistencia")

with st.sidebar:
    st.header("👥 Nuevo Proceso")
    department = st.selectbox("Departamento", ["IT", "RRHH", "Operaciones", "Ventas", "Todas"])
    change_type = st.selectbox("Tipo de Cambio", ["Digitalización", "Reestructuración", "Fusión", "Nueva Tecnología"])
    st.button("🚀 Iniciar Proceso", type="primary")
    st.info("💡 Datos sintéticos para demo")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Procesos Activos", "5", "+1")
col2.metric("Empleados en Cambio", "234", "+45")
col3.metric("Tasa de Adopción", "78%", "+12%")
col4.metric("Resistencia Detectada", "22%", "-8%")

# Procesos
st.subheader("📋 Procesos de Cambio Activos")
change_df = pd.DataFrame([
    {"ID": "CHG-001", "Departamento": "IT", "Tipo": "Digitalización", "Progreso": "75%", "Adopción": "85%", "Resistencia": "15%", "Estado": "En curso"},
    {"ID": "CHG-002", "Departamento": "RRHH", "Tipo": "Nueva Tecnología", "Progreso": "45%", "Adopción": "68%", "Resistencia": "32%", "Estado": "En curso"},
    {"ID": "CHG-003", "Departamento": "Operaciones", "Tipo": "Reestructuración", "Progreso": "90%", "Adopción": "92%", "Resistencia": "8%", "Estado": "Cierre"},
])
st.dataframe(change_df, use_container_width=True, hide_index=True)

# Gráfico
st.subheader("📊 Adopción vs Resistencia por Departamento")
adoption_df = pd.DataFrame({
    "Departamento": ["IT", "RRHH", "Operaciones", "Ventas"],
    "Adopción": [85, 68, 92, 75],
    "Resistencia": [15, 32, 8, 25]
}).set_index("Departamento")
st.bar_chart(adoption_df, use_container_width=True)

# Alertas
st.subheader("⚠️ Alertas de Cambio")
st.warning("🟡 Departamento RRHH: Resistencia del 32% detectada - Sesión de coaching adicional recomendada")
st.info("🔵 Proceso CHG-003 en fase de cierre - 90% completado")
st.success("✅ Tasa de adopción global mejoró 12% este mes")

st.caption(f"Agentes_IA • Change Coaching • {datetime.now().strftime('%Y-%m-%d %H:%M')}")