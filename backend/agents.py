import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

# --- CAMBIO IMPORTANTE: USAMOS TU MODELO DISPONIBLE ---
MODEL_NAME = "gemini-flash-latest" 
# ----------------------------------------------------

def get_rag_context():
    """Carga normas del colegio para saber tipificar la falta"""
    if not os.path.exists(DB_PATH):
        return None
    try:
        embedding_engine = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embedding_engine)
        return vectorstore.as_retriever(search_kwargs={"k": 2})
    except:
        return None

def formatear_historial(historial_chat):
    """Convierte el historial de Gradio a texto plano de forma segura."""
    texto = ""
    for item in historial_chat:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            user_msg = item[0] if item[0] is not None else ""
            bot_msg = item[1] if item[1] is not None else ""
            texto += f"USUARIO: {user_msg}\nASISTENTE: {bot_msg}\n"
    return texto

# --- AGENTE 1: EL RECOPILADOR ---
def responder_alumno(historial_chat, mensaje_nuevo):
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.4, safety_settings=SAFETY_SETTINGS)
    
    retriever = get_rag_context()
    contexto_normas = ""
    if retriever:
        try:
            docs = retriever.invoke(mensaje_nuevo)
            contexto_normas = "\n".join([d.page_content for d in docs])
        except:
            pass

    prompt_template = """
    Eres 'Say It', la herramienta oficial de reporte del centro escolar.
    Tu misión es RECOPILAR INFORMACIÓN OBJETIVA.
    
    CONTEXTO (RAG): {contexto}
    
    OBJETIVOS:
    1. Aclarar si es VÍCTIMA o TESTIGO.
    2. Identificar VÍCTIMA y AGRESORES.
    3. Identificar LUGAR y TIPO de agresión.
    
    DIRECTRICES:
    - Sé directo. Pregunta lo que falte.
    - No des consejos psicológicos, solo recopila hechos.
    
    HISTORIAL:
    {historial}
    
    USUARIO: {pregunta}
    ASISTENTE:
    """
    
    historial_texto = formatear_historial(historial_chat)
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "contexto": contexto_normas,
        "historial": historial_texto,
        "pregunta": mensaje_nuevo
    })

# --- AGENTE 2: EL ANALISTA (Generador de Informe) ---
def generar_reporte_riesgo(chat_completo):
    llm_analista = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0.0,
        safety_settings=SAFETY_SETTINGS
    )
    
    prompt_analisis = """
    Analiza esta denuncia escolar y extrae un JSON.
    Responde SOLO con el JSON.
    
    CAMPOS:
    - "rol_informante": "VÍCTIMA" o "TESTIGO".
    - "nombre_victima": Nombre o "El propio informante".
    - "nombre_agresores": Nombres.
    - "tipo_incidente": Físico, Verbal, Ciberacoso, Exclusión.
    - "resumen_hechos": Resumen cronológico (máx 30 palabras).
    - "nivel_gravedad": LEVE, MODERADO, GRAVE.

    CHAT:
    {chat}
    """
    
    texto_chat = formatear_historial(chat_completo)
    prompt = ChatPromptTemplate.from_template(prompt_analisis)
    chain = prompt | llm_analista | StrOutputParser()
    
    try:
        resultado = chain.invoke({"chat": texto_chat})
        # Limpieza de markdown
        resultado = resultado.replace("```json", "").replace("```", "").strip()
        return json.loads(resultado)
    except Exception as e:
        print(f"Error JSON: {e}")
        return {
            "rol_informante": "Desconocido",
            "resumen_hechos": "Error de procesamiento IA.",
            "nivel_gravedad": "REVISAR"
        }