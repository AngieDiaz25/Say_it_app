from dotenv import load_dotenv
import os
import google.generativeai as genai

# 1. Cargar entorno
load_dotenv()
key = os.getenv("GOOGLE_API_KEY")

print("-" * 30)
if key:
    print(f"🔑 Clave detectada: {key[:5]}...******")

    # 2. Probar conexión real
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Di 'Conexión Exitosa' si me lees.")
        print(f"✅ RESPUESTA DE GOOGLE: {response.text}")
    except Exception as e:
        print(f"❌ Error conectando con Google: {e}")
else:
    print("❌ NO se encontró ninguna clave en el archivo .env")
    print("Asegúrate de que el archivo se llame exactamente '.env' y esté en la carpeta raíz.")
print("-" * 30)