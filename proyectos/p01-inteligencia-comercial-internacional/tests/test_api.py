import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.clients import get_clients

try:
    print("Creando clientes...")
    tavily, groq = get_clients()
    print("✅ Clientes creados")
    
    print("Probando Tavily...")
    result = tavily.search(query="Mexico economy", max_results=1)
    print("✅ Tavily responde")
    
    print("Probando Groq...")
    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=5
    )
    print("✅ Groq responde")
    print("\n🎉 ¡TODO FUNCIONA!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    print(traceback.format_exc())