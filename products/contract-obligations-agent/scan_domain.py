import sys
import os
from pathlib import Path

# Añadir raíz al path
sys.path.insert(0, str(Path.cwd()))

print("🔍 Escaneando domain/ para encontrar módulo principal...")

domain_path = Path("domain")
if domain_path.exists():
    for item in domain_path.iterdir():
        if item.suffix == ".py" and item.stem != "__init__":
            print(f"  ✅ Encontrado: domain.{item.stem}")
            # Intentar importar
            try:
                module = __import__(f"domain.{item.stem}", fromlist=[""])
                print(f"     📦 Clases disponibles: {[x for x in dir(module) if not x.startswith('_')][:5]}")
            except Exception as e:
                print(f"     ⚠️  Error al importar: {e}")
else:
    print("❌ domain/ no encontrado")
