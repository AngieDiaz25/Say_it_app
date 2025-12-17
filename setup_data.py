from main import app, db
from backend.models import CentroEstudios, Director, Profesor, Alumno, Tutor
import os

def cargar_datos_prueba():
    with app.app_context():
        print("🌱 Conectando a la base de datos...")
        
        # 1. Crear tablas si no existen
        db.create_all()
        print("✅ Estructura de tablas verificada.")

        print("🌱 Iniciando carga de datos...")
        
        # 2. Crear Director PRIMERO (para que tenga ID 1)
        if not Director.query.filter_by(email_director="director@sayit.test").first():
            director = Director(
                nombre_director="Sr. Director",
                email_director="director@sayit.test",
                password_hash="12345" 
                # Quitamos id_centro_estudios porque no existe en tu modelo
            )
            db.session.add(director)
            print("➡️ Director creado.")
        
        # Guardamos para asegurar que el Director tenga ID asignado
        db.session.commit() 

        # 3. Crear Centro de Estudios (y vincularlo al Director ID 1)
        centro = CentroEstudios.query.get(1)
        if not centro:
            centro = CentroEstudios(
                id_centro_estudios=1,
                denominacion_generica_es="Instituto",
                denominacion_especifica="Say It Demo",
                id_director=1  # Aquí vinculamos al director que acabamos de crear
            )
            db.session.add(centro)
            print("➡️ Centro creado.")

        # 4. Crear Profesor (Vinculado al Centro ID 1)
        if not Profesor.query.filter_by(email_profesor="profe@sayit.test").first():
            profe = Profesor(
                nombre_profesor="Profe Matemáticas",
                email_profesor="profe@sayit.test",
                password_hash="12345",
                id_centro_estudios=1, # Este sí tiene la columna en tu modelo
                # Quitamos es_tutor si no está en tu modelo (no lo vi en tu código)
            )
            db.session.add(profe)
            print("➡️ Profesor creado.")

        # 5. Crear Alumno (Vinculado al Centro ID 1)
        if not Alumno.query.filter_by(email_alumno="alumno@sayit.test").first():
            alumno = Alumno(
                nombre_alumno="Micaela Alumna",
                email_alumno="alumno@sayit.test",
                password_hash="12345",
                id_centro_estudios=1,
                id_tutor=None 
            )
            db.session.add(alumno)
            print("➡️ Alumno creado.")

        try:
            db.session.commit()
            print("🚀 ¡Datos guardados correctamente! Ya puedes probar el Login.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error guardando datos: {e}")

if __name__ == "__main__":
    cargar_datos_prueba()