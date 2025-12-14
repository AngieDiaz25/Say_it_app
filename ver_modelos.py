import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar la llave
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: No hay API Key en .env")
else:
    # Configurar Google
    genai.configure(api_key=api_key)

    print("\n--- 📋 TUS MODELOS DISPONIBLES ---")
    try:
        encontrado = False
        for m in genai.list_models():
            # Filtramos solo los que sirven para chatear (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                encontrado = True
        
        if not encontrado:
            print("⚠️ No se encontraron modelos compatibles.")
            
    except Exception as e:
        print(f"❌ Error al listar: {e}")