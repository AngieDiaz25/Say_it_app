from flask import Flask, request, jsonify, render_template
from flask_cors import CORS 
import os
from datetime import datetime
from dotenv import load_dotenv

# --- Carga de Entorno ---
load_dotenv()

app = Flask(__name__)
CORS(app) 

# --- IMPORTACIONES DEL BACKEND ---
try:
    from backend.models import db, Alumno, Profesor, Director, Tutor, Informe
    from backend.auth import autenticar_usuario
    # Importamos la IA y el generador de PDF
    from backend.agents import responder_alumno, generar_reporte_riesgo
    from backend.reporting import generar_pdf_informe
except ImportError as e:
    print(f"❌ Error importando backend: {e}")
    exit()

# --- CONFIGURACIÓN DE BASE DE DATOS ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(base_dir, 'bullying.db')
os.makedirs(base_dir, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --------------------------------------------------------------------
# RUTAS
# --------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'status': 'error', 'message': "Faltan datos."}), 400

    with app.app_context():
        rol, user_name = autenticar_usuario(email, password)
        
        if rol == "error":
            return jsonify({'status': 'error', 'message': "Credenciales incorrectas."}), 401
        
        frontend_rol = "alumno"
        if rol in ["profesor", "director"]: frontend_rol = "profesor"
        if rol == "tutor": frontend_rol = "padre"
        
        return jsonify({
            'status': 'success',
            'rol': frontend_rol,
            'user_email': email,
            'user_name': user_name,
            'message': f"Hola {user_name}. Sesión iniciada."
        }), 200

# --- RUTA DEL CHATBOT (CONECTADA A GEMINI) ---
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    mensaje_usuario = data.get('pregunta')
    usuario_email = data.get('usuario') # Email del usuario para contexto (opcional)

    print(f"💬 Chat recibido: {mensaje_usuario}")

    # Llamamos a la función de tu agents.py
    # Nota: Pasamos una lista vacía [] como historial por ahora para simplificar.
    # Si quieres memoria, tendríamos que guardar el historial en el frontend o DB.
    respuesta_ia = responder_alumno([], mensaje_usuario)

    return jsonify({
        'status': 'success', 
        'respuesta': respuesta_ia
    }), 200

# --- RUTA DE REPORTE (CONECTADA A PDF Y DB) ---
# --- RUTA DE REPORTE (CORREGIDA) ---
@app.route('/api/generar-reporte', methods=['POST'])
def api_generar_reporte():
    data = request.get_json()
    texto_incidente = data.get('texto_incidente')
    email_denunciante = data.get('user_email')
    
    print(f"📝 Generando reporte para: {email_denunciante}")

    with app.app_context():
        # 1. Analizar riesgo con IA (agents.py)
        # Convertimos el texto en una lista simulando un chat para la función
        try:
            datos_analisis = generar_reporte_riesgo([("Usuario", texto_incidente)])
        except Exception as e:
            print(f"⚠️ Error IA: {e}")
            datos_analisis = {} # Datos por defecto si falla la IA

        # --- CORRECCIÓN: LIMPIEZA DE DATOS ---
        # Si la IA devuelve una lista ['Ciber'], la convertimos a string "Ciber"
        raw_tipo = datos_analisis.get('tipo_incidente', 'No especificado')
        if isinstance(raw_tipo, list):
            tipo_bullying_str = ", ".join(raw_tipo) # Convierte ['A', 'B'] en "A, B"
        else:
            tipo_bullying_str = str(raw_tipo)
        # -------------------------------------
        
        # 2. Guardar en Base de Datos
        nuevo_informe = Informe(
            tipo_bullying=tipo_bullying_str, # Usamos la versión corregida
            descripcion=texto_incidente,
            id_centro_estudios=1, 
            id_director=1         
        )
        db.session.add(nuevo_informe)
        db.session.commit()

        # 3. Generar PDF (reporting.py)
        ruta_pdf = generar_pdf_informe(
            id_informe=nuevo_informe.id_informe,
            fecha_reporte=datetime.now().strftime("%Y-%m-%d"),
            datos_ia=datos_analisis,
            nombre_centro="Instituto Demo Say It",
            id_centro=1,
            id_director=1,
            nombre_director="Director General",
            id_docente=None,
            nombre_docente="N/A",
            id_alumno=None,
            nombre_alumno=email_denunciante or "Anónimo"
        )

    return jsonify({
        'status': 'success', 
        'mensaje': f"Reporte #{nuevo_informe.id_informe} guardado y PDF generado."
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🚀 SERVIDOR SAY IT ACTIVO EN: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)