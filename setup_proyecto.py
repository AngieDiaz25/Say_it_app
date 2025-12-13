"""
setup_proyecto.py
Script para crear la estructura completa del proyecto
Ejecutar: python setup_proyecto.py
"""

import os
import sys

def crear_estructura():
    """Crea toda la estructura de carpetas del proyecto"""
    
    carpetas = [
        # Backend
        'backend',
        'backend/auth',
        'backend/data_science',
        'backend/security',
        
        # Data
        'data',
        
        # Documentos para RAG
        'documentos_rag',
        
        # Base de datos vectorial
        'chroma_db',
        
        # Logs
        'logs',
        
        # Tests
        'tests',
        'tests/data_science',
        'tests/security',
        
        # Frontend
        'frontend',
        'frontend/static',
        'frontend/templates',
        
        # Docs
        'docs',
        
        # Reports generados
        'reports',
    ]
    
    print("🚀 Creando estructura de carpetas...")
    for carpeta in carpetas:
        os.makedirs(carpeta, exist_ok=True)
        # Crear __init__.py en carpetas de Python
        if 'backend' in carpeta or 'tests' in carpeta:
            init_file = os.path.join(carpeta, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'"""{carpeta} module"""\n')
        print(f"✓ {carpeta}")
    
    print("\n✅ Estructura de carpetas creada")

def crear_gitignore():
    """Crea archivo .gitignore"""
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Entorno virtual
venv/
ENV/

# Variables de entorno
.env
.env.local
.env.*.local

# Base de datos
*.db
*.sqlite
*.sqlite3
data/*.db

# ChromaDB
chroma_db/

# Logs
logs/*.log
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Reports generados
reports/*.pdf
reports/*.html

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Testing
.pytest_cache/
.coverage
htmlcov/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✓ .gitignore creado")

def crear_env_example():
    """Crea archivo .env.example"""
    
    env_content = """# API Keys
GOOGLE_API_KEY=tu_api_key_de_gemini_aqui

# Flask
FLASK_SECRET_KEY=genera_una_clave_secreta_aleatoria
FLASK_ENV=development
FLASK_DEBUG=True

# JWT
JWT_SECRET_KEY=genera_otra_clave_secreta_diferente
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hora en segundos

# Base de datos
DATABASE_URL=sqlite:///data/bullying.db

# Email (configurar más adelante)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_de_app

# Configuración de seguridad
ENCRYPTION_KEY=genera_clave_fernet_aqui
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    
    print("✓ .env.example creado")
    print("⚠️  IMPORTANTE: Copia .env.example a .env y completa con tus API keys")

def crear_readme():
    """Crea README.md mejorado"""
    
    readme_content = """# 🛡️ Say It App - Sistema Anti-Bullying

Aplicación móvil multiagente con LLM, RAG y Reporte Automatizado para denuncia de bullying en centros educativos.

## 🎯 Características

- **Chatbot Empático** con Gemini AI
- **Sistema RAG** para información contextualizada
- **Generación Automática de Informes** en PDF
- **Envío Automático de Emails** a perfiles autorizados
- **Seguridad Robusta** con JWT y encriptación
- **Sistema de Roles** (Estudiante, Profesor, Coordinador, Admin)

## 🚀 Instalación Rápida
```bash
# 1. Clonar repositorio
git clone https://github.com/AngieDiaz25/Say_it_app.git
cd Say_it_app

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\\Scripts\\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 5. Crear estructura del proyecto
python setup_proyecto.py

# 6. Inicializar base de datos
python backend/data_science/generar_datos_sinteticos.py

# 7. Ejecutar aplicación
python main.py
```

## 📁 Estructura del Proyecto
```
Say_it_app/
├── backend/
│   ├── auth/              # Sistema de autenticación
│   ├── data_science/      # LLM, RAG, Chatbot
│   └── security/          # Seguridad y encriptación
├── frontend/              # Interfaz Gradio
├── data/                  # Base de datos
├── documentos_rag/        # Documentos para RAG
├── chroma_db/            # Vector database
├── logs/                  # Logs del sistema
├── reports/              # Informes generados
└── tests/                # Tests automatizados
```

## 🔑 Obtener API Key de Gemini

1. Ir a: https://makersuite.google.com/app/apikey
2. Crear proyecto
3. Obtener API key
4. Agregar a `.env`: `GOOGLE_API_KEY=tu_clave`

## 👥 Equipo

- **Data Science**: Desarrollo de LLM, RAG y generación de informes
- **Ciberseguridad**: Autenticación, encriptación y protección de datos

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add some AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Contacto

Proyecto: [https://github.com/AngieDiaz25/Say_it_app](https://github.com/AngieDiaz25/Say_it_app)
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✓ README.md actualizado")

def main():
    """Ejecuta la configuración inicial"""
    
    print("=" * 60)
    print("  CONFIGURACIÓN INICIAL - SAY IT APP  ")
    print("  Sistema Anti-Bullying con IA  ")
    print("=" * 60)
    print()
    
    try:
        crear_estructura()
        print()
        crear_gitignore()
        crear_env_example()
        crear_readme()
        
        print("\n" + "=" * 60)
        print("✅ ¡CONFIGURACIÓN COMPLETADA!")
        print("=" * 60)
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Copia .env.example a .env")
        print("2. Completa las API keys en .env")
        print("3. Ejecuta: pip install -r requirements.txt")
        print("4. Ejecuta: python backend/data_science/generar_datos_sinteticos.py")
        print("5. Ejecuta: python main.py")
        print("\n🚀 ¡Listo para comenzar el desarrollo!")
        
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()