# 🛡️ Say It App - Sistema Anti-Bullying

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
venv\Scripts\activate  # Windows

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
