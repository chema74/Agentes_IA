# products/asistente-legal-supervisado/app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Legal Counsel", layout="wide", page_icon="⚖️")

st.title("⚖️ Autonomous Legal Counsel Agent")
st.caption("Asesoramiento legal • Análisis de contratos • Consultas jurídicas • Supervisión humana")

with st.sidebar:
    st.header("⚖️ Nueva Consulta")
    query_type = st.selectbox("Tipo", ["Contrato Laboral", "Propiedad Intelectual", "Protección de Datos", "Litigio Comercial", "Mercantil"])
    urgency = st.select_slider("Urgencia", options=["Baja", "Media", "Alta", "Crítica"])
    st.button("📝 Enviar Consulta", type="primary")
    st.info("💡 Datos sintéticos para demo")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Consultas Procesadas", "25", "+5")
col2.metric("Respuestas Generadas", "23", "92%")
col3.metric("Revisión Humana", "2", "⚠️")
col4.metric("Confianza Promedio", "87%", "+3%")

# Consultas recientes
st.subheader("📋 Consultas Recientes")
queries_df = pd.DataFrame([
    {"ID": "Q-001", "Tipo": "Contrato Laboral", "Estado": "Completada", "Confianza": "92%", "Riesgo": "Bajo", "Tiempo": "15 min"},
    {"ID": "Q-002", "Tipo": "Propiedad Intelectual", "Estado": "Revisión Humana", "Confianza": "65%", "Riesgo": "Alto", "Tiempo": "45 min"},
    {"ID": "Q-003", "Tipo": "Protección de Datos", "Estado": "Completada", "Confianza": "88%", "Riesgo": "Medio", "Tiempo": "20 min"},
    {"ID": "Q-004", "Tipo": "Litigio Comercial", "Estado": "Completada", "Confianza": "91%", "Riesgo": "Bajo", "Tiempo": "30 min"},
])
st.dataframe(queries_df, use_container_width=True, hide_index=True)

# Gráfico
st.subheader("📊 Distribución de Consultas por Tipo")
type_df = pd.DataFrame({"Tipo": ["Laboral", "PI", "Datos", "Litigio"], "Count": [8, 5, 7, 5]}).set_index("Tipo")
st.bar_chart(type_df, use_container_width=True)

# Alertas
st.subheader("⚠️ Recomendaciones Legales")
st.warning("🟡 Consulta de PI requiere validación por especialista humano - Complejidad alta")
st.info("🔵 Cambio regulatorio en protección de datos entra en vigor 2026-06-01")
st.success("✅ 23 consultas resueltas sin intervención humana esta semana")

st.caption(f"Agentes_IA • Legal Counsel • {datetime.now().strftime('%Y-%m-%d %H:%M')}")