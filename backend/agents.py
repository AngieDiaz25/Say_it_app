import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
# --- CORRECCIÓN AQUÍ: Usamos langchain_core ---
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# ----------------------------------------------

# Cargar entorno
load_dotenv()

# Rutas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DB_PATH = os.path.join(BASE_DIR, "data/vector_store")

# Seguridad (OFF para permitir reporte de violencia)
SAFETY_SETTINGS = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
}

def get_rag_context():
    """Carga normas del colegio para saber tipificar la falta"""
    if not os.path.exists(DB_PATH):
        return None
    embedding_engine = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embedding_engine)
    return vectorstore.as_retriever(search_kwargs={"k": 2})

# --- AGENTE 1: EL RECOPILADOR (Entrevistador) ---
def responder_alumno(historial_chat, mensaje_nuevo):
    """
    Este agente actúa como un OFICIAL DE TOMA DE DATOS.
    Su prioridad es aclarar los hechos para el reporte.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.4, safety_settings=SAFETY_SETTINGS)
    
    retriever = get_rag_context()
    contexto_normas = ""
    if retriever:
        docs = retriever.invoke(mensaje_nuevo)
        contexto_normas = "\n".join([d.page_content for d in docs])

    prompt_template = """
    Eres 'Say It', la herramienta oficial de reporte del centro escolar.
    Tu misión es RECOPILAR INFORMACIÓN OBJETIVA para generar un informe de denuncia.
    
    CONTEXTO DEL PROTOCOLO ESCOLAR:
    {contexto}
    
    TUS OBJETIVOS DE ENTREVISTA:
    1. Aclarar el ROL: ¿El usuario es la VÍCTIMA o un TESTIGO?
    2. Identificar a la VÍCTIMA (si es un testigo quien habla).
    3. Identificar a los AGRESORES (Nombres o descripción).
    4. Identificar el TIPO y LUGAR de la agresión.
    
    DIRECTRICES:
    - Sé directo pero amable. Agradece la valentía de reportar.
    - Si faltan datos clave (ej: "¿Quién lo hizo?"), PREGUNTA por ellos.
    - NO des consejos psicológicos profundos, enfócate en los hechos.
    
    HISTORIAL:
    {historial}
    
    USUARIO: {pregunta}
    
    ASISTENTE (Responde corto y enfocado en obtener datos):
    """
    
    historial_texto = ""
    for user_msg, bot_msg in historial_chat:
        historial_texto += f"USUARIO: {user_msg}\nASISTENTE: {bot_msg}\n"

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "contexto": contexto_normas,
        "historial": historial_texto,
        "pregunta": mensaje_nuevo
    })

# --- AGENTE 2: EL ANALISTA DE DATOS (Generador de Informe) ---
def generar_reporte_riesgo(chat_completo):
    """
    Lee el chat y estructura los datos para el Director.
    Diferencia si quien reporta es testigo o víctima.
    """
    llm_analista = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.0,
        safety_settings=SAFETY_SETTINGS,
        response_mime_type="application/json"
    )
    
    prompt_analisis = """
    Actúa como Analista de Incidencias Escolares.
    Analiza esta transcripción de denuncia y extrae un JSON con los hechos probados.
    
    CAMPOS REQUERIDOS EN EL JSON:
    - "rol_informante": (String) "VÍCTIMA" (si habla de sí mismo) o "TESTIGO" (si reporta algo que vio).
    - "nombre_victima": (String) El nombre de la persona agredida. Si es el propio usuario y no dijo su nombre, pon "El propio informante".
    - "nombre_agresores": (String) Nombres de los culpables detectados.
    - "tipo_incidente": (String) Físico, Verbal, Ciberacoso, Exclusión.
    - "resumen_hechos": (String) Descripción técnica y cronológica de lo sucedido (máx 30 palabras).
    - "nivel_gravedad": (String) LEVE, MODERADO, GRAVE.

    TRANSCRIPCIÓN DEL CHAT:
    {chat}
    """
    
    texto_chat = ""
    for user, bot in chat_completo:
        texto_chat += f"Usuario: {user}\nIA: {bot}\n"

    prompt = ChatPromptTemplate.from_template(prompt_analisis)
    chain = prompt | llm_analista | StrOutputParser()
    
    try:
        return json.loads(chain.invoke({"chat": texto_chat}))
    except:
        return {
            "rol_informante": "Indeterminado",
            "resumen_hechos": "Error al procesar reporte.",
            "nivel_gravedad": "MANUAL"
        }