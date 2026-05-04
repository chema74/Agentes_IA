"""
P09 - Evaluador de Ideas de Negocio
====================================
Autor : Jose Maria
Stack : Groq  Tavily  Streamlit
Coste : Gratuito

CMO FUNCIONA:
  1. Describes tu idea de negocio
  2. Tavily busca informacion actualizada del mercado
  3. Groq analiza viabilidad, mercado, competencia, riesgos y oportunidades
  4. Genera un informe estructurado con puntuacion y plan de validacion
"""

import os, json
from pathlib import Path
from datetime import datetime
import streamlit as st
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="P09 - Evaluador de Ideas de Negocio",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,300&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:#0c0c10;color:#e4e2dc}
.stApp{background:#0c0c10}#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:2rem;padding-bottom:2rem;max-width:1100px}
.app-tag{font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;color:#d4a84b;margin-bottom:.75rem}
.app-title{font-family:'Fraunces',serif;font-size:2.2rem;font-weight:900;line-height:1.1;margin:0}
.app-title em{font-style:italic;font-weight:300;color:#d4a84b}
.app-subtitle{color:#8c8a84;font-size:.9rem;margin-top:.5rem}
.app-header{border-bottom:1px solid rgba(212,168,75,.2);padding-bottom:1.5rem;margin-bottom:2rem}
.groq-badge{display:inline-flex;align-items:center;gap:.4rem;font-family:'DM Mono',monospace;font-size:.6rem;color:#4dd488;border:1px solid rgba(77,212,136,.25);padding:.2rem .6rem;margin-left:.75rem}
.tavily-badge{display:inline-flex;align-items:center;gap:.4rem;font-family:'DM Mono',monospace;font-size:.6rem;color:#68a8e8;border:1px solid rgba(90,150,212,.25);padding:.2rem .6rem;margin-left:.5rem}
.stTextInput>label,.stTextArea>label,.stSelectbox>label{font-family:'DM Mono',monospace !important;font-size:.7rem !important;letter-spacing:.12em !important;text-transform:uppercase !important;color:#d4a84b !important}
.stTextInput input,.stTextArea textarea{background:#14141c !important;border:1px solid rgba(212,168,75,.25) !important;border-radius:3px !important;color:#e4e2dc !important}
[data-baseweb="select"]>div{background:#14141c !important;border:1px solid rgba(212,168,75,.25) !important;border-radius:3px !important;color:#e4e2dc !important}
.stButton>button{background:#d4a84b !important;color:#0c0c10 !important;border:none !important;border-radius:3px !important;font-family:'DM Mono',monospace !important;font-size:.75rem !important;font-weight:700 !important;letter-spacing:.1em !important;text-transform:uppercase !important;padding:.65rem 2rem !important}
.stButton>button:hover{background:#e8c97a !important;transform:translateY(-1px)}

/* Scorecard */
.score-card{background:#14141c;border:1px solid rgba(212,168,75,.2);padding:2rem;text-align:center;position:relative;overflow:hidden}
.score-card::before{content:'';position:absolute;top:0;left:2rem;right:2rem;height:2px;background:linear-gradient(90deg,transparent,#d4a84b,transparent)}
.score-num{font-family:'Fraunces',serif;font-size:4rem;font-weight:900;line-height:1}
.score-label{font-family:'DM Mono',monospace;font-size:.65rem;color:#8c8a84;text-transform:uppercase;letter-spacing:.12em;margin-top:.4rem}
.veredicto{font-family:'DM Mono',monospace;font-size:.75rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:.3rem .9rem;border-radius:2px;margin-top:.6rem;display:inline-block}

/* Bloques de analisis */
.analysis-block{background:#14141c;border:1px solid rgba(212,168,75,.15);padding:1.5rem;margin-bottom:1rem;position:relative}
.analysis-block::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(180deg,#d4a84b,transparent)}
.block-title{font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7a5e28;margin-bottom:.6rem}
.block-text{font-size:.9rem;color:#e4e2dc;line-height:1.85}

/* Itemas */
.item-pos{padding:.45rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem;color:#a8e8c0}
.item-neg{padding:.45rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem;color:#e8b8b8}
.item-neu{padding:.45rem 0;border-bottom:1px solid rgba(212,168,75,.07);font-size:.875rem;color:#c8c6c0}

/* Dimensiones */
.dim-row{display:flex;align-items:center;gap:1rem;padding:.5rem 0;border-bottom:1px solid rgba(212,168,75,.06)}
.dim-label{font-family:'DM Mono',monospace;font-size:.62rem;color:#8c8a84;width:160px;flex-shrink:0}
.dim-bar-bg{flex:1;height:5px;background:rgba(212,168,75,.1);border-radius:3px;overflow:hidden}
.dim-bar-fill{height:100%;border-radius:3px}
.dim-score{font-family:'DM Mono',monospace;font-size:.65rem;width:30px;text-align:right}

/* Pasos de validacion */
.paso-card{border:1px solid rgba(212,168,75,.12);background:#0f0f18;padding:1.1rem 1.25rem;margin-bottom:.5rem;display:flex;align-items:flex-start;gap:1rem}
.paso-num{font-family:'Fraunces',serif;font-size:1.4rem;font-weight:700;color:rgba(212,168,75,.3);flex-shrink:0;line-height:1.2}
.paso-content h4{font-family:'DM Mono',monospace;font-size:.68rem;color:#d4a84b;margin-bottom:.25rem}
.paso-content p{font-size:.85rem;color:#c8c6c0;line-height:1.7}

.custom-divider{height:1px;background:linear-gradient(90deg,transparent,rgba(212,168,75,.3),transparent);margin:1.5rem 0}
.app-footer{font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;text-align:center;padding-top:2rem}
[data-testid="stSidebar"]{background:#10101a !important;border-right:1px solid rgba(212,168,75,.12) !important}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_clients():
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not groq_api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y anade tu clave antes de evaluar ideas."
        )
    if not tavily_api_key:
        raise RuntimeError(
            "Falta TAVILY_API_KEY. Copia .env.example a .env y anade tu clave antes de buscar mercado."
        )
    return Groq(api_key=groq_api_key), TavilyClient(api_key=tavily_api_key)


def buscar_mercado(tavily, idea, sector, mercado):
    """Busca informacion actualizada del mercado para la idea."""
    queries = [
        f"mercado {sector} {mercado} tamano tendencias 2024 2025",
        f"startups empresas {idea[:60]} competidores Espana",
    ]
    fragmentos = []
    for q in queries:
        try:
            r = tavily.search(query=q, max_results=3, search_depth="basic", include_raw_content=False)
            for res in r.get("results", []):
                fragmentos.append(f"- {res.get('title','')}: {res.get('content','')[:250]}")
        except:
            pass
    return "\n".join(fragmentos[:8])


def evaluar_idea(groq_client, idea, sector, mercado, capital, experiencia, info_web):
    """Groq evalua la idea de negocio en profundidad."""

    prompt = f"""Eres un consultor de estrategia empresarial e inversor de capital riesgo con 20 anos de experiencia.
Evala esta idea de negocio con rigor y honestidad. No seas condescendiente: da una valoracin real.

IDEA DE NEGOCIO: {idea}
SECTOR: {sector}
MERCADO OBJETIVO: {mercado}
CAPITAL DISPONIBLE: {capital}
EXPERIENCIA DEL EMPRENDEDOR: {experiencia}

INFORMACIN DE MERCADO ACTUALIZADA:
{info_web}

Genera un JSON exhaustivo con:

resumen_ejecutivo: 3-4 frases de valoracin directa y honesta

puntuacion_global: numero del 1 al 10

veredicto: "Adelante" o "Refinar antes de lanzar" o "Replantear" o "No recomendado"

dimensiones: objeto con puntuacion (1-10) para cada una de:
  - oportunidad_mercado
  - diferenciacion
  - viabilidad_financiera
  - facilidad_ejecucion
  - timing

propuesta_de_valor: 2-3 frases sobre qu problema resuelve y para quien

mercado_objetivo: descripcion del cliente ideal y tamano estimado del mercado

fortalezas: lista de 3-4 puntos fuertes reales de la idea

debilidades: lista de 3-4 debilidades o puntos ciegos crticos

oportunidades: lista de 3 oportunidades concretas a explotar

amenazas: lista de 3 amenazas o riesgos del mercado

competidores_clave: lista de 3-4 competidores directos o sustitutos con 1 frase cada uno

modelo_de_negocio_sugerido: cmo monetizar, 2-3 frases

inversion_estimada: rango de inversion inicial necesaria

tiempo_primer_ingreso: estimacin realista de cundo generar los primeros ingresos

plan_validacion: lista de 5 pasos concretos y ordenados para validar la idea con el minimo riesgo antes de invertir todo el capital

consejo_experto: 2-3 frases del consejo mas importante que daras a este emprendedor

Solo JSON valido. Sin markdown."""

    r = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )
    raw = r.choices[0].message.content.strip()
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"): raw = part; break
    s = raw.find("{"); e = raw.rfind("}")
    if s != -1: raw = raw[s:e+1]
    return json.loads(raw)


def score_color(score):
    if score >= 7.5: return "#4dd488"
    if score >= 5:   return "#d4a84b"
    return "#e87878"


#  SIDEBAR 
with st.sidebar:
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:#d4a84b;margin-bottom:1.25rem">// Contexto del emprendedor</div>', unsafe_allow_html=True)

    sector    = st.selectbox("Sector", [
        "Tecnologa / SaaS", "Comercio y retail", "Servicios profesionales",
        "Formacion y educacion", "Salud y bienestar", "Alimentacion",
        "Turismo y hostelera", "Industria y manufactura", "Otro"
    ])
    mercado   = st.text_input("Mercado geografico", placeholder="Ej: Andalucia  Espana  Europa")
    capital   = st.selectbox("Capital disponible", [
        "Menos de 5.000", "5.000 - 20.000", "20.000 - 100.000",
        "100.000 - 500.000", "Ms de 500.000", "Por determinar"
    ])
    experiencia = st.selectbox("Experiencia en el sector", [
        "Sin experiencia previa", "1-3 anos", "3-10 anos",
        "Ms de 10 anos", "Experto en el sector"
    ])

    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#44433f;line-height:1.9;border-top:1px solid rgba(212,168,75,.1);padding-top:1rem;margin-top:1rem">
        <span style="color:#4dd488"></span> Paso 1: Tavily busca info del mercado<br>
        <span style="color:#4dd488"></span> Paso 2: Groq evala en profundidad<br>
        <span style="color:#d4a84b"></span> Tiempo: 20-30 segundos<br>
        <span style="color:#d4a84b"></span> Anlisis honesto, no condescendiente
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:.58rem;color:#44433f;margin-top:1.5rem">
        P09 - Evaluador de ideas de negocio<br>
        <a href="https://github.com/chema74/portfolio-ia-aplicada/tree/main/portfolio/p09-evaluador-ideas-negocio" style="color:#7a5e28">Ver proyecto en GitHub</a>
    </div>""", unsafe_allow_html=True)


#  CABECERA 
st.markdown("""
<div class="app-header">
  <div class="app-tag">P09 - Evaluador de ideas  Portfolio IA Aplicada
    <span class="groq-badge"> Groq  analisis</span>
    <span class="tavily-badge"> Tavily  mercado real</span>
  </div>
  <div class="app-title">Evala tu <em>Idea</em></div>
  <div class="app-subtitle">
    Describe tu idea  analizamos viabilidad, mercado y riesgos  plan de validacion paso a paso
  </div>
</div>""", unsafe_allow_html=True)


#  FORMULARIO 
idea = st.text_area(
    "Describe tu idea de negocio",
    placeholder=(
        "Ej: Plataforma de IA para que las PYMEs andaluzas automaticen "
        "sus procesos administrativos sin necesidad de equipo tecnico propio. "
        "Modelo SaaS con cuota mensual de 200/mes. Clientes objetivo: "
        "empresas de 5-50 empleados del sector servicios."
    ),
    height=130,
)

col_btn, col_info = st.columns([1, 3])
with col_btn:
    evaluar_btn = st.button("Evaluar idea ", use_container_width=True)
with col_info:
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#44433f;padding:.75rem 0;line-height:1.8">
        Cuanto mas detallada sea la descripcin, mas preciso ser el analisis.<br>
        Incluye: qu problema resuelve  para quien  cmo monetiza  qu te diferencia
    </div>""", unsafe_allow_html=True)


#  ANLISIS 
if evaluar_btn:
    if not idea.strip():
        st.warning("Describe tu idea de negocio para evaluarla.")
        st.stop()

    groq_client, tavily_client = get_clients()

    with st.spinner(" Analizando el mercado en tiempo real..."):
        info_web = buscar_mercado(tavily_client, idea, sector, mercado or "Espana")

    with st.spinner(" Evaluando viabilidad con Groq..."):
        try:
            eval_data = evaluar_idea(groq_client, idea, sector, mercado or "Espana",
                                     capital, experiencia, info_web)
        except json.JSONDecodeError:
            st.error("Error al procesar la respuesta. Intntalo de nuevo."); st.stop()
        except Exception as e:
            st.error(f"Error: {e}"); st.stop()

    #  RENDER 
    score    = eval_data.get("puntuacion_global", 5)
    veredicto = eval_data.get("veredicto", "Refinar antes de lanzar")
    color_v  = {
        "Adelante":                  "#4dd488",
        "Refinar antes de lanzar":   "#d4a84b",
        "Replantear":                "#e87878",
        "No recomendado":            "#ff5555",
    }.get(veredicto, "#d4a84b")

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # Score + veredicto
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div class="score-card">
          <div class="score-num" style="color:{score_color(score)}">{score}</div>
          <div class="score-label">puntuacion global / 10</div>
          <div class="veredicto" style="color:{color_v};border:1px solid {color_v}40;background:{color_v}10">{veredicto}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        # Dimensiones
        dimas = eval_data.get("dimensiones", {})
        dim_labels = {
            "oportunidad_mercado":  "Oportunidad de mercado",
            "diferenciacion":       "Diferenciacion",
            "viabilidad_financiera": "Viabilidad financiera",
            "facilidad_ejecucion":  "Facilidad de ejecucion",
            "timing":               "Timing / momento",
        }
        st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem">Anlisis por dimensin</div>', unsafe_allow_html=True)
        for key, label in dim_labels.items():
            val = dimas.get(key, 5)
            if isinstance(val, dict): val = val.get("puntuacion", 5)
            col = score_color(val)
            st.markdown(f"""
            <div class="dim-row">
              <span class="dim-label">{label}</span>
              <div class="dim-bar-bg">
                <div class="dim-bar-fill" style="width:{val*10}%;background:{col}"></div>
              </div>
              <span class="dim-score" style="color:{col}">{val}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # Resumen ejecutivo
    st.markdown(f"""
    <div class="analysis-block">
      <div class="block-title"> Resumen ejecutivo</div>
      <div class="block-text">{eval_data.get('resumen_ejecutivo','')}</div>
    </div>""", unsafe_allow_html=True)

    # Propuesta de valor y mercado
    col_pv, col_m = st.columns(2)
    with col_pv:
        st.markdown(f"""
        <div class="analysis-block" style="height:100%">
          <div class="block-title"> Propuesta de valor</div>
          <div class="block-text">{eval_data.get('propuesta_de_valor','')}</div>
        </div>""", unsafe_allow_html=True)
    with col_m:
        st.markdown(f"""
        <div class="analysis-block" style="height:100%">
          <div class="block-title"> Mercado objetivo</div>
          <div class="block-text">{eval_data.get('mercado_objetivo','')}</div>
        </div>""", unsafe_allow_html=True)

    # DAFO
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    c_f, c_d, c_o, c_a = st.columns(4)
    for col_w, (titulo, items, css, emoji) in zip(
        [c_f, c_d, c_o, c_a],
        [
            ("Fortalezas",    eval_data.get("fortalezas",[]),    "item-pos", ""),
            ("Debilidades",   eval_data.get("debilidades",[]),   "item-neg", ""),
            ("Oportunidades", eval_data.get("oportunidades",[]), "item-pos", ""),
            ("Amenazas",      eval_data.get("amenazas",[]),      "item-neg", ""),
        ]
    ):
        with col_w:
            st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem">{emoji} {titulo}</div>', unsafe_allow_html=True)
            for item in items:
                st.markdown(f'<div class="{css}"> {item}</div>', unsafe_allow_html=True)

    # Competidores
    competidores = eval_data.get("competidores_clave", [])
    if competidores:
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem"> Competidores clave</div>', unsafe_allow_html=True)
        cols_c = st.columns(min(len(competidores), 4))
        for col_w, comp in zip(cols_c, competidores):
            with col_w:
                if isinstance(comp, dict):
                    nombre = comp.get("nombre", comp.get("competidor", str(comp)))
                    desc   = comp.get("descripcion", comp.get("nota", ""))
                else:
                    partes = str(comp).split(":")
                    nombre = partes[0].strip()
                    desc   = partes[1].strip() if len(partes) > 1 else ""
                st.markdown(f"""
                <div style="border:1px solid rgba(212,168,75,.12);background:#0f0f18;padding:1rem">
                  <div style="font-family:'DM Mono',monospace;font-size:.68rem;color:#d4a84b;margin-bottom:.3rem">{nombre}</div>
                  <div style="font-size:.8rem;color:#8c8a84;line-height:1.6">{desc}</div>
                </div>""", unsafe_allow_html=True)

    # Modelo de negocio e inversion
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    col_mn, col_inv = st.columns(2)
    with col_mn:
        st.markdown(f"""
        <div class="analysis-block">
          <div class="block-title"> Modelo de negocio sugerido</div>
          <div class="block-text">{eval_data.get('modelo_de_negocio_sugerido','')}</div>
        </div>""", unsafe_allow_html=True)
    with col_inv:
        st.markdown(f"""
        <div style="background:#14141c;border:1px solid rgba(212,168,75,.15);padding:1.5rem">
          <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#7a5e28;margin-bottom:.75rem">DATOS FINANCIEROS ESTIMADOS</div>
          <div style="margin-bottom:.6rem">
            <div style="font-family:'DM Mono',monospace;font-size:.58rem;color:#44433f">Inversion inicial</div>
            <div style="font-size:1rem;font-weight:700;color:#d4a84b">{eval_data.get('inversion_estimada','')}</div>
          </div>
          <div>
            <div style="font-family:'DM Mono',monospace;font-size:.58rem;color:#44433f">Primer ingreso estimado</div>
            <div style="font-size:1rem;font-weight:700;color:#4dd488">{eval_data.get('tiempo_primer_ingreso','')}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Plan de validacion
    pasos = eval_data.get("plan_validacion", [])
    if pasos:
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#7a5e28;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem"> Plan de validacion paso a paso</div>', unsafe_allow_html=True)
        for i, paso in enumerate(pasos, 1):
            if isinstance(paso, dict):
                titulo_paso = paso.get("titulo", paso.get("paso", f"Paso {i}"))
                desc_paso   = paso.get("descripcion", paso.get("accion", ""))
            else:
                partes = str(paso).split(":", 1)
                titulo_paso = partes[0].strip()
                desc_paso   = partes[1].strip() if len(partes) > 1 else ""
            st.markdown(f"""
            <div class="paso-card">
              <div class="paso-num">{i:02d}</div>
              <div class="paso-content">
                <h4>{titulo_paso}</h4>
                <p>{desc_paso}</p>
              </div>
            </div>""", unsafe_allow_html=True)

    # Consejo del experto
    consejo = eval_data.get("consejo_experto", "")
    if consejo:
        st.markdown(f"""
        <div style="background:rgba(212,168,75,.05);border:1px solid rgba(212,168,75,.2);padding:1.5rem 2rem;margin-top:1rem;position:relative">
          <div style="position:absolute;top:0;left:2rem;right:2rem;height:2px;background:linear-gradient(90deg,transparent,#d4a84b,transparent)"></div>
          <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#7a5e28;margin-bottom:.5rem">
             Consejo del experto
          </div>
          <div style="font-family:'Fraunces',serif;font-size:1rem;font-weight:300;font-style:italic;color:#c8c6c0;line-height:1.85">
            "{consejo}"
          </div>
        </div>""", unsafe_allow_html=True)

    # Exportar
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    txt = f"EVALUACIN DE IDEA DE NEGOCIO\n{datetime.now().strftime('%d/%m/%Y')}\n{'='*60}\n\n"
    txt += f"IDEA: {idea[:200]}\nSECTOR: {sector}  MERCADO: {mercado}\n\n"
    txt += f"PUNTUACIN GLOBAL: {score}/10  {veredicto}\n\n"
    txt += f"RESUMEN:\n{eval_data.get('resumen_ejecutivo','')}\n\n"
    txt += f"FORTALEZAS:\n" + "\n".join([f" {f}" for f in eval_data.get("fortalezas",[])]) + "\n\n"
    txt += f"DEBILIDADES:\n" + "\n".join([f" {d}" for d in eval_data.get("debilidades",[])]) + "\n\n"
    txt += f"PLAN DE VALIDACIN:\n" + "\n".join([f"{i+1}. {p if isinstance(p,str) else p.get('titulo','')}" for i,p in enumerate(pasos)]) + "\n\n"
    txt += f"CONSEJO: {consejo}\n\n{'='*60}\nGenerado con IA  Portfolio IA Aplicada  Jose Maria  Sevilla"

    st.download_button(
        " Descargar evaluacin (.txt)",
        data=txt,
        file_name=f"evaluacion_idea_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
    )

else:
    # Estado inicial
    st.markdown("""
    <div style="border:1px dashed rgba(212,168,75,.2);padding:3rem 2rem;text-align:center;margin-top:1rem">
      <div style="font-size:2.5rem;margin-bottom:1rem"></div>
      <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#8c8a84;margin-bottom:.75rem">
        Describe tu idea y recibe un analisis honesto en 30 segundos
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:.63rem;color:#44433f;letter-spacing:.06em;line-height:2">
        Viabilidad  mercado  competencia  DAFO  modelo de negocio<br>
        Inversion estimada  tiempo al primer ingreso  plan de validacion<br>
        <span style="color:#4dd488"> Anlisis con datos de mercado en tiempo real  no halagos genricos</span>
      </div>
    </div>""", unsafe_allow_html=True)


st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="app-footer">P09 - Evaluador de Ideas de Negocio  '
    'Groq + Tavily  Portfolio IA Aplicada  Jose Maria  Sevilla</div>',
    unsafe_allow_html=True,
)
