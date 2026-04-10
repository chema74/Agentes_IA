"""Test completo del pipeline para diagnosticar el error."""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.clients import get_clients
from infrastructure.retry import with_retry
from domain.search import buscar_info
from domain.analysis import analizar_pais
from domain.parser import clean_json
from domain.scoring import calcular_scores

tavily, groq = get_clients()
pais, sector, tipo = "México", "General", "PYME exportadora"

print("=== 1. Búsqueda Tavily ===")
try:
    busqueda = with_retry(lambda: buscar_info(tavily, pais, sector), label=f"Tavily:{pais}")
    contexto, fuentes = busqueda["contexto"], busqueda["fuentes"]
    print(f"OK — {len(fuentes)} fuentes encontradas")
except Exception as e:
    print("ERROR:", traceback.format_exc())
    sys.exit(1)

print("\n=== 2. Scoring LLM ===")
try:
    scoring = with_retry(lambda: calcular_scores(contexto, groq=groq), label=f"Scoring:{pais}")
    print("OK — scores:", list(scoring["scores"].keys()))
except Exception as e:
    print("ERROR:", traceback.format_exc())
    sys.exit(1)

print("\n=== 3. Análisis narrativo LLM ===")
try:
    raw_narrativa = with_retry(
        lambda: analizar_pais(groq, pais, sector, tipo, contexto), label=f"LLM:{pais}"
    )
    print("OK — respuesta raw (primeros 300 chars):")
    print(repr(raw_narrativa[:300]))
except Exception as e:
    print("ERROR:", traceback.format_exc())
    sys.exit(1)

print("\n=== 4. Parser JSON ===")
try:
    data = clean_json(raw_narrativa)
    print("OK — claves:", list(data.keys()))
except Exception as e:
    print("ERROR:", traceback.format_exc())
    print("Raw que falló:", repr(raw_narrativa[:500]))
