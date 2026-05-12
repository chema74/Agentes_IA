# products/agente-logistica-autonoma/app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="A2A Logistics", layout="wide", page_icon="🚚")

st.title("🚚 A2A Self-Healing Logistics Agent")
st.caption("Continuidad logística • Detección de disrupciones • Recuperación A2A • Governance-as-code")

with st.sidebar:
    st.header("🌍 Simulación de Disrupción")
    origin = st.selectbox("Origen", ["Shanghai", "Rotterdam", "Hamburgo", "Singapur", "Los Angeles"])
    disruption = st.selectbox("Tipo", ["Retraso puerto", "Fallo proveedor", "Clima adverso", "Bloqueo aduanero"])
    severity = st.slider("Severidad", 1, 10, 5)
    st.button("🔄 Simular Escenario", type="primary")
    st.info("💡 Datos sintéticos para demo")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Disrupciones Activas", "2", "+1")
col2.metric("SLA Promedio", "94.3%", "-0.8%")
col3.metric("Recuperaciones Exitosas", "1", "Hoy")
col4.metric("Coste Medio Recuperación", "+5.7%", "Estable")

# Disrupciones
st.subheader("🚨 Disrupciones Detectadas")
disruptions_df = pd.DataFrame([
    {"ID": "DIS-001", "Origen": "Shanghai", "Tipo": "Retraso puerto", "Delay": "48h", "Riesgo SLA": "Alto", "Estado": "Detectada"},
    {"ID": "DIS-002", "Origen": "Rotterdam", "Tipo": "Fallo proveedor", "Delay": "12h", "Riesgo SLA": "Medio", "Estado": "Evaluada"},
    {"ID": "DIS-003", "Origen": "Hamburgo", "Tipo": "Clima adverso", "Delay": "6h", "Riesgo SLA": "Bajo", "Estado": "Resuelta"},
])
st.dataframe(disruptions_df, use_container_width=True, hide_index=True)

# Planes de recuperación
st.subheader("♻️ Planes de Recuperación A2A")
recovery_df = pd.DataFrame([
    {"Plan": "REC-001", "Disrupción": "DIS-001", "Estrategia": "Rerouting vía Singapur", "Peer": "Peer-APAC-03", "Coste Delta": "+12%", "SLA Recovery": "95%", "Estado": "Negociando"},
    {"Plan": "REC-002", "Disrupción": "DIS-002", "Estrategia": "Proveedor alternativo local", "Peer": "Peer-EU-07", "Coste Delta": "+5%", "SLA Recovery": "99%", "Estado": "Ejecutado"},
])
st.dataframe(recovery_df, use_container_width=True, hide_index=True)

# Gráfico
st.subheader("📊 Impacto en SLA por Disrupción")
chart_df = pd.DataFrame({"Disrupción": ["DIS-001", "DIS-002", "DIS-003"], "Impacto SLA": [3, 2, 1]}).set_index("Disrupción")
st.bar_chart(chart_df, use_container_width=True)

# Timeline
st.subheader("🕐 Timeline de Eventos A2A")
st.text("08:15 - 🔍 Disrupción DIS-001 detectada en puerto Shanghai")
st.text("08:17 - 🤖 Evaluación de riesgo SLA iniciada")
st.text("08:19 - 🔗 Peer APAC-03 descubierto vía A2A protocol")
st.text("08:22 - 💬 Negociación de capacidad alternativa iniciada")
st.text("08:25 - ✅ Plan REC-001 aprobado bajo governance-as-code")

st.caption(f"Agentes_IA • A2A Logistics • {datetime.now().strftime('%Y-%m-%d %H:%M')}")