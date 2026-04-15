import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = str(BASE_DIR / "chroma_db_p03")
COLLECTION_NAME = "licitaciones"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
MODEL_NAME = "llama-3.3-70b-versatile"

# Parámetros de procesamiento
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K = 6
MAX_TEXTO_ANALISIS = 5000
