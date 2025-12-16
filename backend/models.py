from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# --- MODELOS ---

class Director(db.Model):
    __tablename__ = 'directores'
    id_director = db.Column(Integer, primary_key=True)
    nombre_director = db.Column(String(100))
    email_director = db.Column(String(100))
    telefono_director = db.Column(String(20))
    pass_director = db.Column(String(255))

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
    id_director = db.Column(Integer, ForeignKey('directores.id_director'))

class Clase(db.Model):
    __tablename__ = 'clase'
    id_clase = db.Column(Integer, primary_key=True)
    nombre_clase = db.Column(String(50))

class Tutor(db.Model):
    __tablename__ = 'tutor'
    id_tutor = db.Column(Integer, primary_key=True)
    nombre_tutor = db.Column(String(100))
    email_tutor = db.Column(String(100))
    telefono_tutor = db.Column(String(20))
    pass_tutor = db.Column(String(255))

class Profesor(db.Model):
    __tablename__ = 'profesor'
    id_profesor = db.Column(Integer, primary_key=True)
    nombre_profesor = db.Column(String(100))
    mail_profesor = db.Column(String(100))
    pass_profesor = db.Column(String(255))
    id_clase = db.Column(Integer, ForeignKey('clase.id_clase'))

class Alumno(db.Model):
    __tablename__ = 'alumno'
    id_alumno = db.Column(Integer, primary_key=True)
    nombre_alumno = db.Column(String(100))
    anyo_nacimiento_alumno = db.Column(Integer)
    pass_alumno = db.Column(String(255))
    id_centro_estudios = db.Column(Integer, ForeignKey('centro_estudios.id_centro_estudios'))
    id_tutor = db.Column(Integer, ForeignKey('tutor.id_tutor'))
    id_clase = db.Column(Integer, ForeignKey('clase.id_clase'))

class Informe(db.Model):
    __tablename__ = 'informe'
    id_informe = db.Column(Integer, primary_key=True)
    fecha_informe = db.Column(DateTime, default=datetime.utcnow)
    tipo_bullying = db.Column(String(50))
    descripcion = db.Column(String(1000))
    estado = db.Column(String(20), default="Pendiente")  # Pendiente, En Proceso, Resuelto
    id_centro_estudios = db.Column(Integer, ForeignKey('centro_estudios.id_centro_estudios'))
    id_director = db.Column(Integer, ForeignKey('directores.id_director'))