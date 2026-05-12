
"""Template base reutilizable para dashboards de agentes."""
import streamlit as st
import pandas as pd

def create_agent_dashboard(
    agent_name: str,
    agent_title: str,
    agent_icon: str,
    metrics: dict,
    chart_data: pd.DataFrame | None = None,
    table_data: list | None = None,
    alerts: list | None = None,
    sidebar_config: dict | None = None
):
    """
    Crea un dashboard Streamlit estandarizado para cualquier agente.
    """
    # Configuración de página — solo se puede llamar una vez por script
    st.set_page_config(page_title=agent_title, layout="wide", page_icon=agent_icon)
    
    # Header: Título y subtítulos
    st.title(f"{agent_icon} {agent_title}")
    st.caption("Demo visual • Local-first • Sin GPU requerida • Datos sintéticos")
    
    # Sidebar: Configuración dinámica
    with st.sidebar:
        st.header("⚙️ Configuración")
        if sidebar_config:
            for key, config in sidebar_config.items():
                if config['type'] == 'text':
                    st.text_input(config['label'], config['default'], key=key)
                elif config['type'] == 'number':
                    st.number_input(config['label'], value=config['default'], key=key)
                elif config['type'] == 'slider':
                    st.slider(config['label'], config['min'], config['max'], config['value'], key=key)
        
        st.divider() # Un toque visual extra
        st.info("💡 Los datos son sintéticos para demo")
    
    # Métricas principales: Filas dinámicas según el dict recibido
    if metrics:
        cols = st.columns(len(metrics))
        for i, (name, value) in enumerate(metrics.items()):
            # [Inferencia] El delta es puramente estético para la demo visual
            delta = f"+{i+1} nuevo" if i == 0 else f"-{i*5}%" if i % 2 == 0 else "Estable"
            cols[i].metric(name.replace("_", " ").title(), value, delta)
    
    # Gráfico de barras: Solo si hay data disponible
    if chart_data is not None:
        st.subheader("📊 Distribución")
        st.bar_chart(chart_data, use_container_width=True)
    
    # Tabla de resultados: Conversión segura de lista a DataFrame
    if table_data is not None:
        st.subheader("📋 Resultados Detallados")
        # Aquí eliminamos los errores de sintaxis y referencias a st.table
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Sección de Alertas: Lógica de colores basada en palabras clave
    if alerts:
        st.subheader("⚠️ Alertas y Recomendaciones")
        for alert in alerts:
            low_alert = alert.lower()
            if any(word in low_alert for word in ["crítico", "alto", "error"]):
                st.error(alert)
            elif any(word in low_alert for word in ["medio", "pendiente", "aviso"]):
                st.warning(alert)
            else:
                st.info(alert)
    
    # Footer: Créditos y links
    st.markdown("---")
    footer_url = f"https://github.com/chema74/Agentes_IA/tree/main/products/{agent_name}"
    st.caption(f"Generado por Agentes_IA • [{agent_name}]({footer_url})")

# --- Ejemplo de uso (para testeo rápido) ---
# if __name__ == "__main__":
#     create_agent_dashboard(
#         "analizador_pro", "Analizador Pro", "🤖", 
#         {"eficiencia": "98%", "latencia": "12ms"}
#     )