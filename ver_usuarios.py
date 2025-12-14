import os
from flask import Flask
from backend.models import db, Alumno, Director

# Configuración
app = Flask(__name__)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(base_dir, 'bullying.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def listar_usuarios():
    with app.app_context():
        print("\n--- 📋 LISTA DE USUARIOS VÁLIDOS ---")
        
        # 1. Alumnos
        print("\n🎓 ALUMNOS (Copia el nombre EXACTO):")
        alumnos = Alumno.query.limit(5).all()
        for a in alumnos:
            # Mostramos si la contraseña es el hash largo o si es "1234"
            pass_status = "✅ Es '1234'" if a.pass_alumno == "1234" else "🔒 Encriptada (Usa reset_passwords.py)"
            print(f"   👤 Usuario: '{a.nombre_alumno}'  |  Contraseña: {pass_status}")

        # 2. Directores
        print("\n👔 DIRECTORES (Copia el email EXACTO):")
        directores = Director.query.limit(5).all()
        for d in directores:
            pass_status = "✅ Es '1234'" if d.pass_director == "1234" else "🔒 Encriptada (Usa reset_passwords.py)"
            print(f"   📧 Usuario: '{d.email_director}' |  Contraseña: {pass_status}")

if __name__ == "__main__":
    listar_usuarios()