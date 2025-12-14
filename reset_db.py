from backend.models import db, Alumno, CentroEstudios, Director, Tutor, Informe
from main import app
import os

# Borrar base de datos antigua
db_path = os.path.join("data", "bullying.db")
if os.path.exists(db_path):
    os.remove(db_path)
    print("🗑️  Base de datos antigua eliminada.")

with app.app_context():
    db.create_all()
    print("✅ Tablas creadas con la NUEVA estructura.")

    # 1. Crear Director
    director = Director(
        nombre_director="Sr. Director General",
        email_director="admin@sayitapp.com",
        password_hash="1234" # En prod usar hash real
    )
    db.session.add(director)
    db.session.commit() # Commit para tener ID

    # 2. Crear Centro (Vinculado al Director)
    centro = CentroEstudios(
        denominacion_generica_es="Instituto de Educación Secundaria",
        denominacion_especifica="Rafael Alberti",
        id_director=director.id_director # Vinculación clave
    )
    db.session.add(centro)
    db.session.commit()

    # 3. Crear Tutor
    tutor = Tutor(
        nombre_tutor="Juan Tutor",
        email_tutor="tutor@sayit.edu",
        password_hash="1234",
        id_centro_estudios=centro.id_centro_estudios
    )
    db.session.add(tutor)
    db.session.commit()

    # 4. Crear Alumno (Micaela) - Vinculada a Centro y Tutor
    alumno = Alumno(
        nombre_alumno="Micaela Hervia",
        email_alumno="micaela.hervia@sayit.edu",
        password_hash="1234",
        id_centro_estudios=centro.id_centro_estudios,
        id_tutor=tutor.id_tutor
    )
    db.session.add(alumno)
    db.session.commit()

    print(f"🚀 Usuarios creados:")
    print(f"   - Alumno: micaela.hervia@sayit.edu / 1234")
    print(f"   - Director: admin@sayitapp.com / 1234")
    print("✅ RESET COMPLETADO. Ya puedes ejecutar main.py")