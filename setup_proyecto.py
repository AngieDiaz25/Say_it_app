import os

def crear_estructura():
    print("--- 🏗️ Creando Arquitectura del Proyecto 'Say It' ---")

    # Lista de carpetas a crear
    carpetas = [
        "backend/auth",
        "backend/data_science",
        "backend/security",
        "data",
        "documentos_rag",
        "frontend/static",
        "frontend/templates",
        "logs",
        "tests/data_science",
        "tests/security",
        "docs"
    ]

    # Lista de archivos a crear (si no existen)
    archivos = [
        "backend/__init__.py",
        "backend/models.py",
        "backend/auth/__init__.py",
        "backend/data_science/__init__.py",
        "backend/data_science/generar_datos_sinteticos.py",
        "backend/data_science/crear_documentos_rag.py",
        "backend/security/__init__.py",
        "docs/arquitectura_data_science.md",
        "documentos_rag/protocolo_antibullying.txt",
        "documentos_rag/tipos_de_bullying.txt",
        ".env",
        ".env.example",
        "main.py"
    ]

    # 1. Crear Carpetas
    for carpeta in carpetas:
        os.makedirs(carpeta, exist_ok=True)
        print(f"✅ Carpeta creada: {carpeta}")

    # 2. Crear Archivos vacíos (para rellenar luego)
    for archivo in archivos:
        if not os.path.exists(archivo):
            with open(archivo, 'w') as f:
                pass # Solo lo crea vacío
            print(f"📄 Archivo creado: {archivo}")
        else:
            print(f"⚠️ Archivo ya existía: {archivo}")

    print("\n🚀 ¡Estructura finalizada! Ahora toca rellenar el código.")

if __name__ == "__main__":
    crear_estructura()