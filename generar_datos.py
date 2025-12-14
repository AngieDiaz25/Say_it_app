import os
import random
from flask import Flask
from backend.models import db, Alumno, CentroEstudios, Director, Tutor, Profesor, Clase, Informe

# Configuración
app = Flask(__name__)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(base_dir, 'bullying.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Datos Sintéticos
NOMBRES = ["Micaela", "Javier", "Lucía", "Carlos", "Ana", "Pedro", "Sofía", "Miguel", "Elena", "David"]
APELLIDOS = ["Hervia", "García", "López", "Martínez", "Sánchez", "Pérez", "Gómez", "Ruiz", "Díaz", "Fernández"]

def generar_email(nombre, apellido):
    # Genera emails tipo: nombre.apellido@sayit.edu
    return f"{nombre.lower()}.{apellido.lower()}@sayit.edu"

def poblar_bd():
    # 1. Limpieza inicial
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ Base de datos antigua eliminada.")

    with app.app_context():
        db.create_all()
        print("🏗️ Tablas creadas.")

        # 2. Crear DIRECTOR
        dir1 = Director(
            nombre_director="Director General", 
            email_director="admin@sayitapp.com", # LOGIN DIRECTOR
            pass_director="1234",
            telefono_director="600112233"
        )
        db.session.add(dir1)
        db.session.commit() # Commit para obtener ID

        # 3. Crear CENTRO y asignarle el DIRECTOR
        centro1 = CentroEstudios(
            codigo="IES-001",
            denominacion_generica_es="Instituto",
            denominacion_especifica="Rafael Alberti",
            localidad="Madrid",
            id_director=dir1.id_director  # <--- VINCULACIÓN CONFIRMADA
        )
        db.session.add(centro1)
        
        # 4. Crear CLASES
        clases_objs = []
        for nombre_clase in ["1º ESO A", "2º ESO B", "3º ESO C"]:
            c = Clase(nombre_clase=nombre_clase)
            db.session.add(c)
            clases_objs.append(c)
        db.session.commit()

        # 5. Crear TUTOR
        tutor1 = Tutor(
            nombre_tutor="Juan Tutor",
            email_tutor="tutor@sayit.edu", # LOGIN TUTOR
            pass_tutor="1234",
            telefono_tutor="666777888"
        )
        db.session.add(tutor1)
        db.session.commit()

        # 6. Crear PROFESOR
        prof1 = Profesor(
            nombre_profesor="Profesor Severus",
            mail_profesor="profesor@sayit.edu", # LOGIN PROFESOR
            pass_profesor="1234",
            id_clase=clases_objs[0].id_clase
        )
        db.session.add(prof1)

        # 7. Crear ALUMNOS con Email
        print("👥 Generando alumnos con email...")
        for i in range(5):
            if i == 0:
                # Alumno fijo para pruebas fáciles
                nombre = "Micaela"
                apellido = "Hervia"
            else:
                nombre = random.choice(NOMBRES)
                apellido = random.choice(APELLIDOS)
            
            email = generar_email(nombre, apellido)
            
            alumno = Alumno(
                nombre_alumno=f"{nombre} {apellido}",
                email_alumno=email,     # <--- LOGIN ALUMNO
                pass_alumno="1234",
                id_centro_estudios=centro1.id_centro_estudios,
                id_tutor=tutor1.id_tutor,
                id_clase=random.choice(clases_objs).id_clase
            )
            db.session.add(alumno)
            print(f"   -> Creado: {alumno.nombre_alumno} | Email: {email}")

        db.session.commit()
        
        print("\n✅ ¡BASE DE DATOS REGENERADA!")
        print("--------------------------------------------------")
        print("🔑 CREDENCIALES DE PRUEBA (Contraseña siempre '1234'):")
        print("   🎓 Alumno:    micaela.hervia@sayit.edu")
        print("   👔 Director:  admin@sayitapp.com")
        print("   🍎 Profesor:  profesor@sayit.edu")
        print("--------------------------------------------------")

if __name__ == "__main__":
    poblar_bd()