# products/agente-inteligencia-geopolitica/app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Trade Intelligence", layout="wide", page_icon="🌍")

st.title("🌍 Geopolitical Trade Intelligence Agent")
st.caption("Inteligencia comercial • Análisis geopolítico • Riesgo país • Oportunidades de mercado")

with st.sidebar:
    st.header("🔍 Análisis")
    country = st.selectbox("País", ["China", "USA", "Alemania", "Brasil", "India", "México"])
    sector = st.selectbox("Sector", ["Tecnología", "Manufactura", "Energía", "Agricultura", "Servicios"])
    st.button("📊 Analizar Mercado", type="primary")
    st.info("💡 Datos sintéticos para demo")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Mercados Analizados", "15", "+3")
col2.metric("Oportunidades Detectadas", "8", "Esta semana")
col3.metric("Riesgo Promedio", "Medio", "Estable")
col4.metric("Recomendaciones", "5", "Activas")

# Oportunidades
st.subheader("💼 Oportunidades de Mercado Detectadas")
opportunities_df = pd.DataFrame([
    {"País": "India", "Sector": "Tecnología", "Oportunidad": "Expansión IT services", "Riesgo": "Medio", "ROI Est.": "+25%", "Prioridad": "Alta"},
    {"País": "México", "Sector": "Manufactura", "Oportunidad": "Nearshoring automotriz", "Riesgo": "Bajo", "ROI Est.": "+18%", "Prioridad": "Alta"},
    {"País": "Brasil", "Sector": "Agricultura", "Oportunidad": "Agrotech sostenible", "Riesgo": "Medio", "ROI Est.": "+15%", "Prioridad": "Media"},
])
st.dataframe(opportunities_df, use_container_width=True, hide_index=True)

# Gráfico
st.subheader("📊 Riesgo País vs Oportunidad")
risk_df = pd.DataFrame({
    "País": ["China", "USA", "Alemania", "Brasil", "India", "México"],
    "Riesgo": [6, 3, 2, 5, 4, 3],
    "Oportunidad": [7, 6, 5, 6, 8, 7]
}).set_index("País")
st.bar_chart(risk_df, use_container_width=True)

# Alertas
st.subheader("⚠️ Alertas Geopolíticas")
st.warning("🟡 Tensión comercial USA-China puede afectar supply chain tecnológico")
st.info("🔵 Acuerdo comercial UE-Mercosur en negociación - Oportunidad para sector agrícola")
st.error("🔴 Sanciones nuevas a Rusia afectan sector energético - Revisar contratos existentes")

st.caption(f"Agentes_IA • Trade Intelligence • {datetime.now().strftime('%Y-%m-%d %H:%M')}")