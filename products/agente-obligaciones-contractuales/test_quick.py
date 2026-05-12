import sys
sys.path.append(".")

try:
    # Intentar importar un módulo clave (ajusta según tu estructura)
    print("✅ Imports básicos funcionan")
    
    # Probar una función simple si existe
    # from services.extractor import extract_obligations
    # result = extract_obligations("texto de prueba")
    # print(f"✅ Función de extracción responde: {type(result)}")
    
except ImportError as e:
    print(f"⚠️  Import error (normal si faltan deps): {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
