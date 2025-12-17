from main import app, db
from backend.models import CentroEstudios, Director, Profesor, Alumno, Tutor
from werkzeug.security import generate_password_hash

def cargar_datos_prueba():
    with app.app_context():
        print("🌱 Iniciando carga de datos de prueba...")
        
        # 1. Crear Centro de Estudios (Si no existe)
        centro = CentroEstudios.query.get(1)
        if not centro:
            centro = CentroEstudios(
                id_centro_estudios=1,
                denominacion_generica_es="Instituto",
                denominacion_especifica="Say It Demo",
                id_director=1
            )
            db.session.add(centro)
            print("✅ Centro creado.")

        # 2. Crear Director (Login: director@sayit.test / 12345)
        if not Director.query.filter_by(email_director="director@sayit.test").first():
            director = Director(
                nombre_director="Sr. Director",
                email_director="director@sayit.test",
                password_hash="12345", # En producción usar hash real
                id_centro_estudios=1
            )
            db.session.add(director)
            print("✅ Director creado.")

        # 3. Crear Profesor (Login: profe@sayit.test / 12345)
        if not Profesor.query.filter_by(email_profesor="profe@sayit.test").first():
            profe = Profesor(
                nombre_profesor="Profe Matemáticas",
                email_profesor="profe@sayit.test",
                password_hash="12345",
                id_centro_estudios=1,
                es_tutor=False
            )
            db.session.add(profe)
            print("✅ Profesor creado.")

        # 4. Crear Alumno (Login: alumno@sayit.test / 12345)
        if not Alumno.query.filter_by(email_alumno="alumno@sayit.test").first():
            alumno = Alumno(
                nombre_alumno="Micaela Alumna",
                email_alumno="alumno@sayit.test",
                password_hash="12345",
                id_centro_estudios=1,
                id_tutor=None 
            )
            db.session.add(alumno)
            print("✅ Alumno creado.")

        try:
            db.session.commit()
            print("🚀 ¡Datos cargados correctamente! Ya puedes probar la app.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error cargando datos: {e}")

if __name__ == "__main__":
    cargar_datos_prueba()