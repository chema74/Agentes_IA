"""
domain/i18n.py
--------------
Responsabilidad: Diccionario central de traducciones y textos de la interfaz.
Permite que el asistente sea multilingüe y mantiene el código de UI limpio.
Inspirado en la Fase 18C del proyecto p01.
"""

from __future__ import annotations
from typing import Dict, Any

# Diccionario maestro de textos
I18N_DATA: Dict[str, Dict[str, Any]] = {
    "es": {
        "ui": {
            "title": "Asistente Ejecutivo IA",
            "subtitle": "Búsqueda web · Análisis PDF · Resúmenes",
            "sidebar_tools": "// Herramientas Activas",
            "sidebar_history": "📁 Historial de Sesiones",
            "btn_new_chat": "Nueva conversación",
            "btn_download": "Descargar Informe Word",
            "input_placeholder": "Pide información, análisis o resúmenes...",
            "loading_thinking": "🤖 El agente está pensando...",
            "loading_tools": "🏗️ Orquestando herramientas...",
            "status_web": "🔍 Buscando en internet...",
            "status_pdf": "📄 Analizando documento...",
            "status_done": "✅ Análisis completado",
            "msg_no_pdf": "⚠️ No hay documento PDF cargado.",
            "msg_welcome": "¡Bienvenido! ¿En qué puedo ayudarte hoy?"
        },
        "tools": {
            "web_name": "Búsqueda Web",
            "web_desc": "Información en tiempo real vía Tavily",
            "pdf_name": "Análisis PDF",
            "pdf_desc": "Extracción y RAG vía PyMuPDF",
            "res_name": "Resúmenes",
            "res_desc": "Generación de briefings ejecutivos"
        }
    },
    "en": {
        "ui": {
            "title": "AI Executive Assistant",
            "subtitle": "Web Search · PDF Analysis · Summaries",
            "sidebar_tools": "// Active Tools",
            "sidebar_history": "📁 Session History",
            "btn_new_chat": "New Conversation",
            "btn_download": "Download Word Report",
            "input_placeholder": "Ask for information, analysis or summaries...",
            "loading_thinking": "🤖 Agent is thinking...",
            "loading_tools": "🏗️ Orchestrating tools...",
            "status_web": "🔍 Searching the web...",
            "status_pdf": "📄 Analyzing document...",
            "status_done": "✅ Analysis completed",
            "msg_no_pdf": "⚠️ No PDF document uploaded.",
            "msg_welcome": "Welcome! How can I help you today?"
        },
        "tools": {
            "web_name": "Web Search",
            "web_desc": "Real-time info via Tavily",
            "pdf_name": "PDF Analysis",
            "pdf_desc": "Extraction & RAG via PyMuPDF",
            "res_name": "Summaries",
            "res_desc": "Executive briefing generation"
        }
    }
}

def get_text(key: str, section: str = "ui", lang: str = "es") -> Any:
    """
    Recupera un texto del diccionario según el idioma seleccionado.
    Si la clave no existe, devuelve el nombre de la clave entre corchetes 
    para facilitar la depuración.
    """
    lang_dict = I18N_DATA.get(lang, I18N_DATA["es"])
    section_dict = lang_dict.get(section, lang_dict.get("ui", {}))
    return section_dict.get(key, f"[{key}]")