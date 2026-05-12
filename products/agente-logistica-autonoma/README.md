# A2A Self-Healing Logistics Agent

Agente API-first para continuidad logística. Detecta disrupciones, descubre peers A2A, negocia capacidad alternativa, evalúa riesgo de SLA y ejecuta recuperaciones bajo governance-as-code.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-orange)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)
![Demo](https://img.shields.io/badge/Demo-Streamlit-orange)

## 🚀 Ejecución Rápida

### Dashboard Visual (Recomendado)
```powershell
cd products/agente-logistica-autonoma
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py