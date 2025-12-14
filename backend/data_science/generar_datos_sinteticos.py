import sys
import os
import random
from faker import Faker
from flask import Flask

# --- TRUCO PARA IMPORTAR DESDE CARPETAS SUPERIORES ---
# Añadimos la raíz del proyecto al path de Python para encontrar 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.models import db, CentroEstudios, Director, Clase, Tutor, Profesor, Alumno, Informe
from backend.auth import hash_password

fake = Faker('es_ES')

def create_fake_app():
    app = Flask(__name__)
    # Ruta absoluta para asegurar que se guarde en la carpeta 'data'
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
    db_path = os.path.join(base_dir, 'bullying.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def generar_datos():
    print("🏭 Generando datos en data/bullying.db ...")
    app = create_fake_app()
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # --- 1. DIRECTORES ---
        directores = []
        for _ in range(3):
            d = Director(
                nombre_director=fake.name(),
                email_director=fake.email(),
                telefono_director=fake.phone_number(),
                pass_director=hash_password("admin123")
            )
            db.session.add(d)
            directores.append(d)
        db.session.commit()
        
        # --- 2. CENTROS ---
        centros = []
        for d in directores:
            c = CentroEstudios(
                codigo=fake.bothify(text='CEN-####'),
                denominacion_generica_es="Instituto", 
                denominacion_generica_val="Institut",
                denominacion_especifica=f"IES {fake.city()}",
                regimen="Público", tipo_via="Calle", direccion=fake.street_name(),
                numero=fake.building_number(), codigo_postal=fake.postcode(),
                localidad="Valencia", provincia="Valencia", telefono=fake.phone_number(),
                longitud=float(fake.longitude()), latitud=float(fake.latitude()),
                comarca="L'Horta", id_director=d.id_director
            )
            db.session.add(c)
            centros.append(c)
        db.session.commit()
        
        # --- 3. CLASES Y PROFESORES ---
        clases = []
        for n in ["1º ESO A", "1º ESO B", "2º ESO A", "3º ESO A"]:
            cl = Clase(nombre_clase=n)
            db.session.add(cl)
            clases.append(cl)
        
        db.session.commit() # Guardar clases primero

        for cl in clases:
            p = Profesor(
                nombre_profesor=fake.name(), mail_profesor=fake.email(),
                pass_profesor=hash_password("profe123"), id_clase=cl.id_clase
            )
            db.session.add(p)
        db.session.commit()

        # --- 4. ALUMNOS Y TUTORES ---
        for _ in range(20):
            t = Tutor(
                nombre_tutor=fake.name(), email_tutor=fake.email(),
                telefono_tutor=fake.phone_number(), pass_tutor=hash_password("tutor123")
            )
            db.session.add(t)
            db.session.flush()
            
            centro = random.choice(centros)
            clase = random.choice(clases)
            
            a = Alumno(
                nombre_alumno=fake.name(), anyo_nacimiento_alumno=random.randint(2008, 2012),
                pass_alumno=hash_password("alumno123"), id_centro_estudios=centro.id_centro_estudios,
                id_tutor=t.id_tutor, id_clase=clase.id_clase
            )
            db.session.add(a)
        
        db.session.commit()
        print("✅ ¡Base de datos regenerada en la nueva estructura!")

if __name__ == "__main__":
    generar_datos()