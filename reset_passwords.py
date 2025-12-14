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

def resetear_claves():
    with app.app_context():
        print("--- 🔄 RESTAURANDO CONTRASEÑAS ---")
        
        # 1. Resetear Director
        director = Director.query.first()
        if director:
            director.pass_director = "1234"
            db.session.commit()
            print(f"✅ DIRECTOR actualizado:")
            print(f"   - Usuario (Email): {director.email_director}")
            print(f"   - Nueva Contraseña: 1234")
        else:
            print("⚠️ No se encontró ningún director.")

        # 2. Resetear Alumno
        alumno = Alumno.query.first()
        if alumno:
            alumno.pass_alumno = "1234"
            db.session.commit()
            print(f"✅ ALUMNO actualizado:")
            print(f"   - Usuario (Nombre): {alumno.nombre_alumno}")
            print(f"   - Nueva Contraseña: 1234")
        else:
            print("⚠️ No se encontró ningún alumno.")
            
if __name__ == "__main__":
    resetear_claves()