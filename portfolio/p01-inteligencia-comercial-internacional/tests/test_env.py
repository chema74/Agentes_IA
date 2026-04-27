import os
from pathlib import Path
from dotenv import load_dotenv

print("=== DIAGNÓSTICO DE VARIABLES DE ENTORNO ===\n")

# 1. Verificar qué hay ANTES de cargar nada
print("1. Variables ANTES de cargar .env:")
print(f"   GROQ_API_KEY: {os.environ.get('GROQ_API_KEY', 'NO EXISTE')[:20] if os.environ.get('GROQ_API_KEY') else 'NO EXISTE'}")

# 2. Calcular dónde debería estar el .env
settings_file = Path(__file__).parent / "config" / "settings.py"
env_file = settings_file.resolve().parent.parent / ".env"

print(f"\n2. Ubicación calculada:")
print(f"   settings.py: {settings_file.resolve()}")
print(f"   .env esperado: {env_file}")
print(f"   ¿Existe?: {env_file.exists()}")

# 3. Leer el archivo .env directamente (sin parser)
if env_file.exists():
    print(f"\n3. Contenido RAW de {env_file}:")
    with open(env_file, 'r') as f:
        for i, line in enumerate(f.readlines()[:5], 1):
            if '=' in line and not line.startswith('#'):
                key = line.split('=')[0]
                val = line.split('=')[1].strip()[:15] if '=' in line else ''
                print(f"   Línea {i}: {key}={val}...")

# 4. Cargar con dotenv
print(f"\n4. Cargando con load_dotenv(override=True)...")
load_dotenv(dotenv_path=env_file, override=True)

# 5. Verificar DESPUÉS
print(f"\n5. Variables DESPUÉS de cargar:")
groq = os.environ.get('GROQ_API_KEY', 'NO CARGADA')
print(f"   GROQ_API_KEY: {groq[:20]}...")

# 6. Comparar con lo que lee settings.py
print(f"\n6. Importando config.settings...")
try:
    from config.settings import GROQ_API_KEY as SETTINGS_GROQ
    print(f"   settings.GROQ_API_KEY: {SETTINGS_GROQ[:20] if SETTINGS_GROQ else 'NO CARGADA'}...")
    
    if groq != SETTINGS_GROQ:
        print(f"\n   ⚠️  ¡DIFERENCIA DETECTADA!")
        print(f"      os.environ: {groq[:15]}...")
        print(f"      settings.py: {SETTINGS_GROQ[:15]}...")
except Exception as e:
    print(f"   Error importando settings: {e}")

print("\n=== FIN DEL DIAGNÓSTICO ===")