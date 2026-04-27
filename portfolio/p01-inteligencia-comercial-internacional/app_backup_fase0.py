"""
P01 · Agente de Análisis de Riesgo País para Exportación
=========================================================
Autor : José María
Stack : Tavily (búsqueda) + Groq (análisis) + Streamlit
Groq  : gratuito en https://console.groq.com

ARQUITECTURA: 2 llamadas separadas en lugar de agente con iteraciones
  1. Tavily busca información del país (3 resultados)
  2. Groq analiza y genera el JSON del informe
"""

import os
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient
from groq import Groq

load_dotenv()

# ─── PÁGINA ───────────────────────────────
st.set_page_config(
    page_title="Riesgo País IA",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,300&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family:'DM Sans',sans-serif; background:#0c0c10; color:#e4e2dc; }
.stApp { background:#0c0c10; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:2rem; padding-bottom:2rem; max-width:1100px; }

.app-tag { font-family:'DM Mono',monospace; font-size:.65rem; letter-spacing:.2em; text-transform:uppercase; color:#d4a84b; margin-bottom:.75rem; }
.app-title { font-family:'Fraunces',serif; font-size:2.4rem; font-weight:900; line-height:1.1; margin:0; }
.app-title em { font-style:italic; font-weight:300; color:#d4a84b; }
.app-subtitle { color:#8c8a84; font-size:.95rem; margin-top:.5rem; }
.app-header { border-bottom:1px solid rgba(212,168,75,.2); padding-bottom:1.5rem; margin-bottom:2.5rem; }

.groq-badge { display:inline-flex; align-items:center; gap:.4rem; font-family:'DM Mono',monospace; font-size:.6rem; color:#4dd488; border:1px solid rgba(77,212,136,.25); padding:.2rem .6rem; margin-left:.75rem; }

.stTextInput > label { font-family:'DM Mono',monospace !important; font-size:.7rem !important; letter-spacing:.12em !important; text-transform:uppercase !important; color:#d4a84b !important; }
.stTextInput input { background:#14141c !important; border:1px solid rgba(212,168,75,.25) !important; border-radius:3px !important; color:#e4e2dc !important; }
.stTextInput input:focus { border-color:#d4a84b !important; box-shadow:0 0 0 2px rgba(212,168,75,.1) !important; }
.stSelectbox > label { font-family:'DM Mono',monospace !important; font-size:.7rem !important; letter-spacing:.12em !important; text-transform:uppercase !important; color:#d4a84b !important; }
[data-baseweb="select"] > div { background:#14141c !important; border:1px solid rgba(212,168,75,.25) !important; border-radius:3px !important; color:#e4e2dc !important; }

.stButton > button { background:#d4a84b !important; color:#0c0c10 !important; border:none !important; border-radius:3px !important; font-family:'DM Mono',monospace !important; font-size:.75rem !important; font-weight:700 !important; letter-spacing:.1em !important; text-transform:uppercase !important; padding:.65rem 2rem !important; transition:all .2s !important; }
.stButton > button:hover { background:#e8c97a !important; transform:translateY(-1px); box-shadow:0 4px 20px rgba(212,168,75,.3) !important; }

.report-section { border:1px solid rgba(212,168,75,.15); background:#14141c; margin-bottom:1rem; position:relative; }
.report-section::before { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background:linear-gradient(180deg,#d4a84b,transparent); }
.report-section-header { padding:1rem 1.5rem; border-bottom:1px solid rgba(212,168,75,.1); display:flex; align-items:center; gap:.75rem; }
.report-section-title { font-family:'DM Mono',monospace; font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color:#d4a84b; }
.report-section-body { padding:1.25rem 1.5rem; font-size:.9rem; color:#c8c6c0; line-height:1.85; }

.alert-box { border:1px solid rgba(232,120,120,.3); background:rgba(232,120,120,.05); padding:1rem 1.25rem; margin-bottom:.75rem; display:flex; gap:.75rem; }
.alert-text { font-size:.85rem; color:#e8b8b8; line-height:1.7; }
.opp-box { border:1px solid rgba(77,212,136,.2); background:rgba(77,212,136,.04); padding:1rem 1.25rem; margin-bottom:.75rem; display:flex; gap:.75rem; }
.opp-text { font-size:.85rem; color:#a8e8c0; line-height:1.7; }

.custom-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent); margin:2rem 0; }
.app-footer { font-family:'DM Mono',monospace; font-size:.62rem; color:#44433f; text-align:center; padding-top:2rem; letter-spacing:.08em; }
[data-testid="stSidebar"] { background:#10101a !important; border-right:1px solid rgba(212,168,75,.12) !important; }
.streamlit-expanderHeader { font-family:'DM Mono',monospace !important; font-size:.72rem !important; color:#d4a84b !important; background:#14141c !important; border:1px solid rgba(212,168,75,.2) !important; }
.streamlit-expanderContent { background:#14141c !important; border:1px solid rgba(212,168,75,.2) !important; border-top:none !important; }
</style>
""", unsafe_allow_html=True)


# ─── CLIENTES ─────────────────────────────
@st.cache_resource
def get_clients():
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    groq   = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return tavily, groq


# ─── LÓGICA PRINCIPAL ─────────────────────
def buscar_info(tavily: TavilyClient, pais: str, sector: str) -> str:
    """Paso 1: Tavily busca información actualizada del país."""
    resultado = tavily.search(
        query=f"{pais} riesgo pais economia politica exportacion {sector} 2024 2025",
        max_results=4,
        search_depth="basic",
        include_raw_content=False,
    )
    # Construir contexto resumido
    fragmentos = []
    for r in resultado.get("results", []): # type: ignore
        titulo   = r.get("title", "")
        contenido = r.get("content", "")[:400]  # máx 400 chars por resultado
        fragmentos.append(f"- {titulo}: {contenido}")

    return "\n".join(fragmentos)


def analizar_pais(groq: Groq, pais: str, sector: str, tipo: str, contexto: str) -> dict:
    """Paso 2: Groq analiza el contexto y genera el informe JSON."""

    prompt = f"""Eres analista de riesgo pais. Con la siguiente informacion reciente, genera un informe JSON.

INFORMACION ACTUAL SOBRE {pais.upper()}:
{contexto}

Genera un JSON valido con exactamente estas claves:
- pais: string
- fecha_analisis: "{datetime.now().strftime('%d/%m/%Y')}"
- scores: objeto con politico, economico, regulatorio, score_global
  (cada uno con: valor 1-10, nivel Bajo/Medio/Alto/Critico, resumen string corto)
- resumen_ejecutivo: string 2-3 frases
- dimension_politica: string 60-80 palabras
- dimension_economica: string 60-80 palabras
- dimension_regulatoria: string 60-80 palabras
- dimension_mercado: string 60-80 palabras para sector {sector}
- alertas: array de 3 strings
- oportunidades: array de 3 strings
- recomendacion: string 1-2 frases para {tipo}

ESCALA RIESGO: 1-3=Bajo 4-5=Medio 6-7=Alto 8-10=Critico
Responde SOLO con el JSON. Sin markdown. Sin texto antes ni despues."""

    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1500,
    )
    return response.choices[0].message.content # type: ignore


def clean_json(raw: str) -> dict:
    """Extrae y parsea el JSON de la respuesta."""
    raw = raw.strip()
    # Quitar bloques markdown
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                raw = part
                break
    # Buscar primer { y último }
    start = raw.find("{")
    end   = raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end+1]
    return json.loads(raw)


# ─── HELPERS DE RENDER ─────────────────────
def risk_color(nivel):
    return {"Bajo":"#4dd488","Medio":"#d4a84b","Alto":"#e89a78",
            "Critico":"#ff5555","Crítico":"#ff5555"}.get(nivel,"#d4a84b")

def risk_emoji(nivel):
    return {"Bajo":"🟢","Medio":"🟡","Alto":"🟠",
            "Critico":"🔴","Crítico":"🔴"}.get(nivel,"⚪")

def render_score_grid(scores):
    dims = [
        ("Riesgo Político",    scores.get("politico",    {})),
        ("Riesgo Económico",   scores.get("economico",   {})),
        ("Riesgo Regulatorio", scores.get("regulatorio", {})),
        ("Score Global",       scores.get("score_global",{})),
    ]
    for col, (label, data) in zip(st.columns(4), dims):
        valor   = data.get("valor", "—")
        nivel   = data.get("nivel", "—")
        resumen = data.get("resumen", "")
        with col:
            st.markdown(f"""
            <div style="background:#14141c;border:1px solid rgba(212,168,75,.15);
                padding:1.5rem 1rem;text-align:center">
              <div style="font-family:'DM Mono',monospace;font-size:.58rem;
                  letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;
                  margin-bottom:.5rem">{label}</div>
              <div style="font-family:'Fraunces',serif;font-size:2.2rem;
                  font-weight:900;line-height:1;color:{risk_color(nivel)}">{valor}</div>
              <div style="font-size:.75rem;margin-top:.4rem">{risk_emoji(nivel)} {nivel}</div>
              {f'<div style="font-size:.68rem;color:#8c8a84;margin-top:.3rem;line-height:1.4">{resumen[:60]}</div>' if resumen else ''}
            </div>""", unsafe_allow_html=True)

def render_section(icon, title, content):
    st.markdown(f"""
    <div class="report-section">
      <div class="report-section-header">
        <span style="font-size:1.1rem">{icon}</span>
        <span class="report-section-title">{title}</span>
      </div>
      <div class="report-section-body">{content}</div>
    </div>""", unsafe_allow_html=True)

def render_items(items, tipo="alerta"):
    for item in items:
        if tipo == "alerta":
            st.markdown(f'<div class="alert-box"><span>⚠️</span><span class="alert-text">{item}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="opp-box"><span>✅</span><span class="opp-text">{item}</span></div>', unsafe_allow_html=True)


# ─── SIDEBAR ──────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem">// Configuración</div>', unsafe_allow_html=True)

    sector = st.selectbox("Sector de exportación", [
        "General","Agroalimentario","Tecnología","Industrial",
        "Servicios profesionales","Textil y moda","Construcción",
        "Energía","Educación y formación","Turismo",
    ])
    tipo_empresa = st.selectbox("Tipo de empresa", [
        "PYME exportadora","Gran empresa","Startup",
        "Organismo público","Consultora",
    ])

    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;
        line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
        <span style="color:#4dd488">●</span> Paso 1: Tavily busca info actual<br>
        <span style="color:#4dd488">●</span> Paso 2: Groq genera el informe<br>
        <span style="color:#4dd488">●</span> Sin agente = sin límite iteraciones<br>
        <span style="color:#d4a84b">●</span> Tiempo estimado: 8-15s
    </div>""", unsafe_allow_html=True)


# ─── CABECERA ─────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-tag">P01 · Análisis de riesgo · Portfolio IA Aplicada
    <span class="groq-badge">⚡ Groq · Llama 3.3 70B · Gratuito</span>
  </div>
  <div class="app-title">Riesgo País <em>Intelligence</em></div>
  <div class="app-subtitle">Informes de riesgo país en tiempo real para apoyar decisiones de exportación</div>
</div>""", unsafe_allow_html=True)


# ─── FORMULARIO ───────────────────────────
col_input, col_btn = st.columns([4, 1])
with col_input:
    pais = st.text_input("País a analizar", placeholder="Ej: México, Vietnam, Arabia Saudí, Marruecos...")
with col_btn:
    st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
    analizar = st.button("Analizar →", use_container_width=True)

st.markdown("""
<div style="display:flex;gap:.5rem;flex-wrap:wrap;margin:.5rem 0 1.5rem">
  <span style="font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.2);color:#7a5e28">Sugerencias →</span>
  <span style="font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.12);color:#8c8a84">México</span>
  <span style="font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.12);color:#8c8a84">Marruecos</span>
  <span style="font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.12);color:#8c8a84">Vietnam</span>
  <span style="font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.12);color:#8c8a84">Arabia Saudí</span>
  <span style="font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.12);color:#8c8a84">Colombia</span>
  <span style="font-family:'DM Mono',monospace;font-size:.6rem;padding:.25rem .7rem;border:1px solid rgba(212,168,75,.12);color:#8c8a84">Turquía</span>
</div>""", unsafe_allow_html=True)


# ─── EJECUCIÓN ────────────────────────────
if analizar and pais.strip():

    tavily_client, groq_client = get_clients()

    # Paso 1 — Búsqueda
    with st.spinner(f"🔍 Buscando información actualizada sobre {pais.strip()}..."):
        try:
            contexto = buscar_info(tavily_client, pais.strip(), sector) # type: ignore
        except Exception as e: 
            st.error(f"Error en búsqueda Tavily: {e}")
            st.stop()

    # Paso 2 — Análisis
    with st.spinner("⚡ Generando informe con Groq..."):
        try:
            raw  = analizar_pais(groq_client, pais.strip(), sector, tipo_empresa, contexto) # type: ignore
            data = clean_json(raw) # type: ignore
        except json.JSONDecodeError:
            st.error("El modelo devolvió una respuesta inesperada. Inténtalo de nuevo.")
            with st.expander("Ver respuesta en bruto"):
                st.code(raw, language="text")
            st.stop()
        except Exception as e:
            st.error(f"Error en análisis Groq: {e}")
            st.stop()

    # ── Render del informe ──
    pais_ok = data.get("pais", pais).upper()
    fecha   = data.get("fecha_analisis", datetime.now().strftime("%d/%m/%Y"))

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:baseline;
        border-bottom:1px solid rgba(212,168,75,.2);padding-bottom:1rem;margin-bottom:1.5rem">
      <div>
        <span style="font-family:'Fraunces',serif;font-size:1.6rem;font-weight:700">{pais_ok}</span>
        <span style="font-family:'DM Mono',monospace;font-size:.62rem;color:#7a5e28;margin-left:1rem;letter-spacing:.1em">INFORME DE RIESGO PAÍS</span>
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f">
        {fecha} · {sector} · {tipo_empresa}
      </div>
    </div>""", unsafe_allow_html=True)

    render_score_grid(data.get("scores", {}))
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    if data.get("resumen_ejecutivo"):
        st.markdown(f"""
        <div style="background:#14141c;border:1px solid rgba(212,168,75,.2);
            padding:1.5rem 2rem;margin-bottom:1.5rem;position:relative">
          <div style="position:absolute;top:0;left:2rem;right:2rem;height:2px;
            background:linear-gradient(90deg,transparent,#d4a84b,transparent)"></div>
          <div style="font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;
            text-transform:uppercase;color:#7a5e28;margin-bottom:.75rem">Resumen ejecutivo</div>
          <div style="font-family:'Fraunces',serif;font-size:1rem;font-weight:300;
            font-style:italic;color:#c8c6c0;line-height:1.85">{data["resumen_ejecutivo"]}</div>
        </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        render_section("🏛️","Dimensión política",     data.get("dimension_politica","—"))
        render_section("📋","Marco regulatorio",       data.get("dimension_regulatoria","—"))
    with c2:
        render_section("📈","Dimensión económica",     data.get("dimension_economica","—"))
        render_section("🤝","Contexto de mercado",     data.get("dimension_mercado","—"))

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    ca, co = st.columns(2)
    with ca:
        st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:#e87878;margin-bottom:1rem">⚠️ Señales de alerta</div>', unsafe_allow_html=True)
        render_items(data.get("alertas",[]), "alerta")
    with co:
        st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:#4dd488;margin-bottom:1rem">✅ Oportunidades</div>', unsafe_allow_html=True)
        render_items(data.get("oportunidades",[]), "opp")

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    if data.get("recomendacion"):
        st.markdown(f"""
        <div style="background:rgba(212,168,75,.06);border:1px solid rgba(212,168,75,.25);padding:1.5rem 2rem">
          <div style="font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#d4a84b;margin-bottom:.75rem">→ Recomendación final</div>
          <div style="font-size:.95rem;color:#e4e2dc;line-height:1.85">{data["recomendacion"]}</div>
        </div>""", unsafe_allow_html=True)

    with st.expander("Ver datos en bruto (JSON)"):
        st.json(data)

elif analizar and not pais.strip():
    st.warning("Introduce el nombre del país que quieres analizar.")

else:
    st.markdown("""
    <div style="border:1px dashed rgba(212,168,75,.2);padding:3rem 2rem;text-align:center;margin-top:1rem">
      <div style="font-size:2.5rem;margin-bottom:1rem">🌍</div>
      <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#8c8a84;margin-bottom:.75rem">
        Introduce un país para comenzar el análisis
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:.63rem;color:#44433f;letter-spacing:.06em;line-height:1.9">
        Paso 1 · Tavily busca información actualizada del país<br>
        Paso 2 · Groq genera el informe estructurado con scores y recomendaciones<br>
        <span style="color:#4dd488">⚡ Powered by Groq — gratuito y ultrarrápido</span>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="app-footer">P01 · Riesgo País Intelligence · Groq + Llama 3.3 70B + Tavily · Portfolio IA Aplicada · José María · Sevilla</div>', unsafe_allow_html=True)