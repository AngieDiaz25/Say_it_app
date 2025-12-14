import os
from dotenv import load_dotenv # <--- Carga las variables de entorno

# Cargar variables del archivo .env si existe
load_dotenv()

# Verificación de seguridad antes de arrancar
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ ERROR CRÍTICO: No se encuentra la GOOGLE_API_KEY.")
    print("   -> Solución: Crea un archivo .env o ejecuta 'export GOOGLE_API_KEY=tu_clave'")
    exit(1)

# --- IMPORTS ---
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Configuración
DB_DIR = "chroma_db"
DOCS_DIR = "documentos_rag"

def inicializar_base_vectorial():
    """Lee los TXT, los trocea y los guarda en la base de datos vectorial."""
    if not os.path.exists(DOCS_DIR):
        print("❌ Error: No hay documentos en documentos_rag/")
        return

    print("--- ⚙️ PROCESANDO NORMATIVA ---")
    
    # 1. Cargar documentos
    loader = DirectoryLoader(DOCS_DIR, glob="*.txt", loader_cls=TextLoader)
    docs = loader.load()
    print(f"📄 Documentos cargados: {len(docs)}")
    
    # 2. Dividir en trozos (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    print(f"🧩 Fragmentos generados: {len(chunks)}")

    # 3. Crear Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # 4. Guardar en ChromaDB (Limpiando la anterior si existe)
    if os.path.exists(DB_DIR):
        import shutil
        shutil.rmtree(DB_DIR) 
            
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=DB_DIR
    )
    # En versiones nuevas de Langchain, persist() a veces es automático, 
    # pero lo dejamos por compatibilidad.
    # vectorstore.persist() 
    
    print("✅ Base de Datos Normativa actualizada correctamente.")

def obtener_contexto_relevante(query):
    """Busca en la BD la información más parecida a la pregunta del usuario."""
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
        
        # Buscar los 2 fragmentos más relevantes
        docs = vectorstore.similarity_search(query, k=2)
        
        contexto = "\n".join([d.page_content for d in docs])
        return contexto
    except Exception as e:
        print(f"⚠️ Error RAG: {e}")
        return ""

if __name__ == "__main__":
    inicializar_base_vectorial()