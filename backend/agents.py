import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
model = None

# --- CONFIGURACION ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Usamos tu modelo disponible
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ IA CONECTADA: Backend listo con Gemini 2.5 Flash")
    except Exception as e:
        print(f"❌ Error configuración IA: {e}")
else:
    print("⚠️ ADVERTENCIA: No se encontró GOOGLE_API_KEY en .env")

# --- PROTOCOLO (RAG MEJORADO Y HUMANIZADO) ---
PROTOCOLO_SEGURIDAD = """
ERES 'SAY IT', UN ASISTENTE VIRTUAL DE CONVIVENCIA ESCOLAR.
TU TONO: Calmado, seguro, confidencial y profesional.

REGLAS DE INTERACCIÓN:

1. FASE DE SALUDO (IMPORTANTE):
   - Si el usuario dice "Hola", "Buenas", o saluda simple: NO asumas inmediatamente que ha pasado algo grave.
   - Respuesta correcta: "Hola. Estoy aquí para escucharte de forma segura y confidencial. ¿Quieres contarme algo o necesitas ayuda?"
   - Respuesta INCORRECTA: "Siento que estés mal" (No lo digas si no sabes qué pasa).

2. FASE DE ESCUCHA (Cuando cuenten el problema):
   - Ahora SÍ muestra empatía: "Siento mucho que estés pasando por eso."
   - Tu objetivo es conseguir 3 datos clave sin parecer un interrogatorio policial:
     A) QUÉ (Descripción de los hechos).
     B) QUIÉN (Nombres o descripción de los agresores).
     C) CUÁNDO/DÓNDE (Fecha y lugar).

3. FASE DE CIERRE:
   - Si tienes los datos o el alumno no quiere hablar más, recuérdale que puede usar el botón "Generar Reporte" para enviar la información a dirección.

EJEMPLO DE FLUJO IDEAL:
- Usuario: "Hola"
- Tú: "Hola. Aquí puedes hablar con confianza. ¿Cómo puedo ayudarte?"
- Usuario: "Es que se meten conmigo"
- Tú: "Lo siento mucho, nadie debería pasar por eso. ¿Puedes decirme quién te está molestando?"
"""

def responder_alumno(historial, mensaje_usuario):
    if not model:
        return "⚠️ Error: IA no conectada."

    try:
        historial_texto = ""
        for item in historial:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                human = item[0]
                ai = item[1]
                if human and ai:
                    historial_texto += f"Alumno: {human}\nSay It: {ai}\n"

        prompt_completo = f"""
        {PROTOCOLO_SEGURIDAD}
        
        HISTORIAL PREVIO:
        {historial_texto}
        
        NUEVO MENSAJE DEL ALUMNO:
        {mensaje_usuario}
        
        TU RESPUESTA (Directa y orientada a conseguir los datos):
        """
        
        response = model.generate_content(prompt_completo)
        return response.text
        
    except Exception as e:
        print(f"🔥 ERROR CHAT: {e}")
        return "Disculpa, he tenido un fallo técnico. ¿Puedes repetirlo?"

def generar_reporte_riesgo(historial_chat):
    if not model:
        raise ConnectionError("Sin API Key")

    chat_str = str(historial_chat)
    prompt_analisis = f"""
    Actúa como analista. Extrae JSON puro de este chat:
    {chat_str}
    
    JSON ESPERADO:
    {{
        "rol_informante": "VÍCTIMA" o "TESTIGO",
        "tipo_incidente": ["Físico", "Verbal", "Ciber"],
        "nivel_gravedad": "LEVE", "MODERADO" o "GRAVE",
        "resumen_hechos": "Resumen en 3 persona (max 30 palabras)",
        "nombres_involucrados": ["Nombres o Desconocido"]
    }}
    """
    
    response = model.generate_content(prompt_analisis)
    texto_limpio = response.text.replace("```json", "").replace("```", 
"").strip()
    return json.loads(texto_limpio)
