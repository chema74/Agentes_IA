"""
settings.py
-----------
Configuración centralizada del Asistente Ejecutivo.
Inspirado en la robustez de arquitecturas industriales (p01).
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# 1. RUTA BASE: Detectamos dónde está el proyecto para que los paths no fallen nunca
#
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. CARGA DE VARIABLES: Apuntamos al .env que ya tienes
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

# 3. CLAVES API: Extraemos con validación básica
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

if not GROQ_API_KEY or not TAVILY_API_KEY:
    # [Inferencia] Lanzamos error temprano para no descubrir el fallo en mitad de una demo
    raise ValueError("⚠️ Faltan las claves API en el archivo .env. Revisa GROQ_API_KEY y TAVILY_API_KEY.")

# 4. CONFIGURACIÓN DEL MODELO (El 'Cerebro')
# Centralizamos aquí para poder saltar a Llama-3.1 o 3.3 sin tocar el código de lógica
#
MODEL_NAME = "llama-3.3-70b-versatile"
TEMPERATURE = 0.2
MAX_TOKENS = 1500

# 5. PARÁMETROS DE BÚSQUEDA (Tavily)
#
MAX_RESULTS_PER_QUERY = 4
SEARCH_DEPTH = "advanced"

# 6. CONFIGURACIÓN DE PROCESAMIENTO DE DOCUMENTOS (RAG)
# [Inferencia] Valores óptimos para que el asistente no pierda el hilo en PDFs largos
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150

# 7. RUTAS DE SALIDA: Para que los informes no se pierdan
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)