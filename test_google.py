import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Cargar la llave desde el archivo .env
load_dotenv() 
api_key = os.getenv("GOOGLE_API_KEY")

print(f"--- DIAGNÓSTICO ---")

if not api_key:
    print("❌ ERROR: No se encontró la 'GOOGLE_API_KEY'.")
    print("Asegúrate de haber creado el archivo .env con tu clave dentro.")
else:
    print(f"✅ Clave detectada: {api_key[:5]}...*****")
    print("Probando conexión con Google (Modelo: gemini-pro)...")
    try:
        # Usamos 'gemini-pro' que es el más compatible
        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
        res = llm.invoke("Di 'Conexión exitosa'")
        print(f"✅ ¡FUNCIONA! Google respondió: {res.content}")
    except Exception as e:
        print(f"❌ FALLO TÉCNICO:\n{e}")