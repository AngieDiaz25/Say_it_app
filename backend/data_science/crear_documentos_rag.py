import sys
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# --- CONFIGURACIÓN DE RUTAS ---
# Calculamos la raíz del proyecto para encontrar las carpetas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DOCS_PATH = os.path.join(BASE_DIR, "documentos_rag")  # Donde están los TXT
DB_PATH = os.path.join(BASE_DIR, "data/vector_store") # Donde guardamos la memoria

# Cargar .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

def indexar_conocimiento():
    print("--- 🧠 Entrenando al Agente (RAG) con Google Gemini ---")
    print(f"📂 Buscando documentos en: {DOCS_PATH}")
    
    # 1. Verificar claves
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: No se encontró GOOGLE_API_KEY en el archivo .env")
        return

    # 2. Cargar documentos
    if not os.path.exists(DOCS_PATH):
        os.makedirs(DOCS_PATH)
        print(f"⚠️ La carpeta {DOCS_PATH} no existía. Créala y pon archivos .txt dentro.")
        return

    loader = DirectoryLoader(DOCS_PATH, glob="*.txt", loader_cls=TextLoader)
    docs = loader.load()
    
    if not docs:
        print("❌ No hay archivos .txt para leer. El cerebro está vacío.")
        print("👉 Crea un archivo .txt con normas en la carpeta 'documentos_rag'.")
        return

    print(f"📄 Leídos {len(docs)} documentos.")

    # 3. Dividir texto (Chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    print(f"✂️  Texto dividido en {len(splits)} fragmentos.")

    # 4. Generar Embeddings y Guardar
    print("🔮 Conectando con Google AI para generar embeddings...")
    try:
        embedding_engine = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding_engine,
            persist_directory=DB_PATH
        )
        print("="*50)
        print(f"✅ ¡CEREBRO ACTUALIZADO! Memoria guardada en: data/vector_store")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error conectando con Google: {e}")

if __name__ == "__main__":
    indexar_conocimiento()