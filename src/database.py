from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

# Configuración básica de SQLAlchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# --- 1. DIRECTORES (Según tu esquema: director@s) ---
class Director(db.Model):
    __tablename__ = 'directores'
    
    id_director = db.Column(Integer, primary_key=True)
    nombre_director = db.Column(String(100))
    email_director = db.Column(String(100))
    telefono_director = db.Column(String(20))
    pass_director = db.Column(String(255)) # Hash de contraseña

# --- 2. CENTRO DE ESTUDIOS ---
class CentroEstudios(db.Model):
    __tablename__ = 'centro_estudios'
    
    id_centro_estudios = db.Column(Integer, primary_key=True)
    codigo = db.Column(String(50))
    denominacion_generica_es = db.Column(String(100))
    denominacion_generica_val = db.Column(String(100))
    denominacion_especifica = db.Column(String(100))
    regimen = db.Column(String(50))
    tipo_via = db.Column(String(50))
    direccion = db.Column(String(200))
    numero = db.Column(String(20))
    codigo_postal = db.Column(String(10))
    localidad = db.Column(String(100))
    provincia = db.Column(String(100))
    telefono = db.Column(String(20))
    longitud = db.Column(Float)
    latitud = db.Column(Float)
    comarca = db.Column(String(100))
    
    # FK hacia Director (Un centro tiene un director asignado)
    id_director = db.Column(Integer, ForeignKey('directores.id_director'))
    # (También pones id_profesor como FK en el diagrama, lo añado como opcional)
    id_profesor_responsable = db.Column(Integer, ForeignKey('profesor.id_profesor'), nullable=True)

# --- 3. CLASE ---
class Clase(db.Model):
    __tablename__ = 'clase'
    
    id_clase = db.Column(Integer, primary_key=True)
    nombre_clase = db.Column(String(50)) # Ej: "1º ESO A"

# --- 4. TUTOR (Padres/Tutores legales) ---
class Tutor(db.Model):
    __tablename__ = 'tutor'
    
    id_tutor = db.Column(Integer, primary_key=True)
    nombre_tutor = db.Column(String(100))
    email_tutor = db.Column(String(100))
    telefono_tutor = db.Column(String(20))
    pass_tutor = db.Column(String(255))
    
    # En tu diagrama, el Tutor tiene FK a Alumno (id_alumno).
    # Pero Alumno TIENE FK a Tutor. Para evitar el problema del "huevo y la gallina",
    # dejaremos la relación fuerte en la tabla ALUMNO (que es lo estándar).
    # Si necesitas buscar al revés, se hace por consulta.

# --- 5. PROFESOR ---
class Profesor(db.Model):
    __tablename__ = 'profesor'
    
    id_profesor = db.Column(Integer, primary_key=True)
    nombre_profesor = db.Column(String(100))
    mail_profesor = db.Column(String(100))
    pass_profesor = db.Column(String(255))
    
    # FK: Un profesor pertenece a una clase (tutoría) según tu diagrama
    id_clase = db.Column(Integer, ForeignKey('clase.id_clase'))

# --- 6. ALUMNO ---
class Alumno(db.Model):
    __tablename__ = 'alumno'
    
    id_alumno = db.Column(Integer, primary_key=True)
    nombre_alumno = db.Column(String(100))
    anyo_nacimiento_alumno = db.Column(Integer)
    pass_alumno = db.Column(String(255))
    
    # Las 3 flechas que llegan a Alumno en tu diagrama:
    id_centro_estudios = db.Column(Integer, ForeignKey('centro_estudios.id_centro_estudios'))
    id_tutor = db.Column(Integer, ForeignKey('tutor.id_tutor'))
    id_clase = db.Column(Integer, ForeignKey('clase.id_clase'))

# --- 7. INFORME (Reportes) ---
class Informe(db.Model):
    __tablename__ = 'informe'
    
    id_informe = db.Column(Integer, primary_key=True)
    fecha_informe = db.Column(DateTime, default=datetime.utcnow)
    tipo_bullying = db.Column(String(50))
    descripcion = db.Column(String(1000)) # Añadido para guardar el texto del reporte
    
    # FKs según diagrama
    id_centro_estudios = db.Column(Integer, ForeignKey('centro_estudios.id_centro_estudios'))
    id_director = db.Column(Integer, ForeignKey('directores.id_director'))