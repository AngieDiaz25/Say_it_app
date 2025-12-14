from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CentroEstudios(db.Model):
    __tablename__ = 'centros_estudios'
    id_centro_estudios = db.Column(db.Integer, primary_key=True)
    denominacion_generica_es = db.Column(db.String(100))
    denominacion_especifica = db.Column(db.String(100))
    id_director = db.Column(db.Integer, nullable=True)

class Director(db.Model):
    __tablename__ = 'directores'
    id_director = db.Column(db.Integer, primary_key=True)
    nombre_director = db.Column(db.String(100))
    email_director = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))

class Tutor(db.Model):
    __tablename__ = 'tutores'
    id_tutor = db.Column(db.Integer, primary_key=True)
    nombre_tutor = db.Column(db.String(100))
    email_tutor = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))
    id_centro_estudios = db.Column(db.Integer, db.ForeignKey('centros_estudios.id_centro_estudios'))

class Profesor(db.Model): # <--- ¡ESTA ES LA CLASE QUE FALTABA!
    __tablename__ = 'profesores'
    id_profesor = db.Column(db.Integer, primary_key=True)
    nombre_profesor = db.Column(db.String(100))
    email_profesor = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))
    id_centro_estudios = db.Column(db.Integer, db.ForeignKey('centros_estudios.id_centro_estudios'))

class Alumno(db.Model):
    __tablename__ = 'alumnos'
    id_alumno = db.Column(db.Integer, primary_key=True)
    nombre_alumno = db.Column(db.String(100))
    email_alumno = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))
    id_centro_estudios = db.Column(db.Integer, db.ForeignKey('centros_estudios.id_centro_estudios'))
    id_tutor = db.Column(db.Integer, db.ForeignKey('tutores.id_tutor'))

class Informe(db.Model):
    __tablename__ = 'informes'
    id_informe = db.Column(db.Integer, primary_key=True)
    tipo_bullying = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_informe = db.Column(db.DateTime, default=datetime.utcnow)
    id_centro_estudios = db.Column(db.Integer)
    id_director = db.Column(db.Integer)