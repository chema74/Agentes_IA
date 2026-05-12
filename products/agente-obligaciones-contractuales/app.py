"""Dashboard ligero con Streamlit para el agente."""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Contract Agent", layout="wide", page_icon="📋")

st.title("📋 Agente de Obligaciones Contractuales")
st.caption("Demo visual • Local-first • Sin GPU requerida")

# Sidebar con controles
with st.sidebar:
    st.header("⚙️ Configuración")
    contract_id = st.text_input("ID Contrato", "CONT-2026-001")
    risk_threshold = st.slider("Umbral de riesgo", 0, 100, 50)
    st.info("💡 Los datos son sintéticos para demo")

# Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Obligaciones", "3", "1 nueva")
col2.metric("Riesgo Promedio", "Medio", "-10%")
col3.metric("Próximo Vencimiento", "15 días", "⚠️")

# Gráfico
st.subheader("📊 Distribución de Riesgos")
df = pd.DataFrame({"Riesgo": ["Bajo", "Medio", "Alto"], "Count": [1, 1, 1]})
st.bar_chart(df.set_index("Riesgo"), use_container_width=True)

# Tabla de obligaciones
st.subheader("📌 Obligaciones Detectadas")
st.dataframe(
    pd.DataFrame([
        {"Tipo": "Pago", "Detalle": "€50,000", "Plazo": "2026-06-30", "Riesgo": "Bajo"},
        {"Tipo": "Entrega", "Detalle": "Módulo reporting", "Plazo": "2026-05-15", "Riesgo": "Medio"},
        {"Tipo": "Confidencialidad", "Detalle": "24 meses", "Plazo": "Post-contrato", "Riesgo": "Alto"}
    ]),
    use_container_width=True,
    hide_index=True
)

# Alertas
st.subheader("⚠️ Alertas")
st.warning("Fecha de entrega cercana (15 días)")
st.error("Cláusula de confidencialidad requiere revisión legal")

st.markdown("---")
st.caption("Generado por Agentes_IA • [Ver código](https://github.com/chema74/Agentes_IA)")