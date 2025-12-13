import os
import random
from faker import Faker
from flask import Flask
# Importamos las clases nuevas desde tu archivo database.py
from src.database import db, CentroEstudios, Director, Clase, Tutor, Profesor, Alumno, Informe
from src.auth import hash_password 

fake = Faker('es_ES')

def create_fake_app():
    # Creamos una app falsa solo para poder usar la base de datos
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///say_it.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def generar_datos_diagrama():
    print("🚀 Iniciando generación de datos (Esquema Oficial)...")
    
    app = create_fake_app()
    with app.app_context():
        # 1. Crear las tablas vacías
        db.create_all()
        
        # --- PASO A: DIRECTORES ---
        print("  -> Creando Directores...")
        directores = []
        for _ in range(3):
            d = Director(
                nombre_director=fake.name(),
                email_director=fake.email(),
                telefono_director=fake.phone_number(),
                pass_director=hash_password("director123")
            )
            db.session.add(d)
            directores.append(d)
        db.session.commit()
        
        # --- PASO B: CENTROS (Necesitan Directores) ---
        print("  -> Creando Centros Educativos...")
        centros = []
        for d in directores:
            c = CentroEstudios(
                codigo=fake.bothify(text='CEN-####'),
                denominacion_generica_es="Instituto Secundaria",
                denominacion_generica_val="Institut Secundària",
                denominacion_especifica=f"IES {fake.city()}",
                regimen="Público",
                tipo_via="Calle",
                direccion=fake.street_name(),
                numero=fake.building_number(),
                codigo_postal=fake.postcode(),
                localidad="Valencia",
                provincia="Valencia",
                telefono=fake.phone_number(),
                longitud=float(fake.longitude()),
                latitud=float(fake.latitude()),
                comarca="L'Horta",
                id_director=d.id_director # Enlazamos con el director creado antes
            )
            db.session.add(c)
            centros.append(c)
        db.session.commit()
        
        # --- PASO C: CLASES ---
        print("  -> Creando Clases...")
        nombres_clases = ["1º ESO A", "1º ESO B", "2º ESO A", "3º ESO A"]
        clases = []
        for n in nombres_clases:
            cl = Clase(nombre_clase=n)
            db.session.add(cl)
            clases.append(cl)
        db.session.commit()
        
        # --- PASO D: PROFESORES (Necesitan Clases) ---
        print("  -> Contratando Profesores...")
        for cl in clases:
            p = Profesor(
                nombre_profesor=fake.name(),
                mail_profesor=fake.email(),
                pass_profesor=hash_password("profe123"),
                id_clase=cl.id_clase
            )
            db.session.add(p)
        db.session.commit()

        # --- PASO E: ALUMNOS Y TUTORES ---
        print("  -> Matriculando Alumnos...")
        for _ in range(15): # Creamos 15 alumnos
            # 1. Creamos su Tutor (Padre/Madre)
            t = Tutor(
                nombre_tutor=fake.name(),
                email_tutor=fake.email(),
                telefono_tutor=fake.phone_number(),
                pass_tutor=hash_password("tutor123")
            )
            db.session.add(t)
            db.session.flush() # Guardar para tener ID
            
            # 2. Creamos al Alumno
            centro_random = random.choice(centros)
            clase_random = random.choice(clases)
            
            a = Alumno(
                nombre_alumno=fake.name(),
                anyo_nacimiento_alumno=random.randint(2008, 2012),
                pass_alumno=hash_password("alumno123"),
                id_centro_estudios=centro_random.id_centro_estudios,
                id_tutor=t.id_tutor,
                id_clase=clase_random.id_clase
            )
            db.session.add(a)
            
            # Imprimimos uno de ejemplo para que puedas probar
            if _ == 0:
                user_ejemplo = a.nombre_alumno
        
        db.session.commit()
        
        print("\n✅ ¡Base de datos regenerada según el diagrama!")
        print(f"👉 Puedes probar con el alumno: {user_ejemplo} (Pass: alumno123)")

if __name__ == "__main__":
    generar_datos_diagrama()