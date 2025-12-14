import os
from flask import Flask
from backend.models import db
from backend.auth import autenticar_usuario

# Configuración mínima para que funcione la base de datos
app = Flask(__name__)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(base_dir, 'bullying.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def probar_credenciales(usuario, password):
    print(f"\n🔍 Probando: Usuario='{usuario}' | Pass='{password}'")
    try:
        rol, nombre = autenticar_usuario(usuario, password)
        if rol == "error":
            print("❌ FALLO: Usuario o contraseña incorrectos.")
        else:
            print(f"✅ ÉXITO: Acceso concedido como '{rol}' (Nombre: {nombre})")
    except Exception as e:
        print(f"💥 ERROR TÉCNICO: {e}")
        import traceback
        traceback.print_exc()

# --- EJECUCIÓN ---
if __name__ == "__main__":
    with app.app_context():
        print("--- DIAGNÓSTICO DE LOGIN ---")
        
        # Caso 1: Alumno (Copia exacta de la BD)
        probar_credenciales("Micaela Hervia", "estudiante")
        
        # Caso 2: Director
        probar_credenciales("admin@sayitapp.com", "admin")