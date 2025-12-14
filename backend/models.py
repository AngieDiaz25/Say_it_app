from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# --- TABLAS DE ESTRUCTURA ---

class CentroEstudios(db.Model):
    __tablename__ = 'centro_estudios'
    id_centro_estudios = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50))
    denominacion_generica_es = db.Column(db.String(100)) 
    denominacion_especifica = db.Column(db.String(100))  
    direccion = db.Column(db.String(200))
    localidad = db.Column(db.String(100))
    provincia = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    id_director = db.Column(db.Integer, db.ForeignKey('directores.id_director'))

class Clase(db.Model):
    __tablename__ = 'clase'
    id_clase = db.Column(db.Integer, primary_key=True)
    nombre_clase = db.Column(db.String(50))

# --- USUARIOS ---

class Director(db.Model):
    __tablename__ = 'directores'
    id_director = db.Column(db.Integer, primary_key=True)
    nombre_director = db.Column(db.String(100))
    email_director = db.Column(db.String(100))
    telefono_director = db.Column(db.String(20))
    pass_director = db.Column(db.String(255))

class Tutor(db.Model):
    __tablename__ = 'tutor'
    id_tutor = db.Column(db.Integer, primary_key=True)
    nombre_tutor = db.Column(db.String(100))
    email_tutor = db.Column(db.String(100))
    telefono_tutor = db.Column(db.String(20))
    pass_tutor = db.Column(db.String(255))

class Profesor(db.Model):
    __tablename__ = 'profesor'
    id_profesor = db.Column(db.Integer, primary_key=True)
    nombre_profesor = db.Column(db.String(100))
    mail_profesor = db.Column(db.String(100))
    pass_profesor = db.Column(db.String(255))
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id_clase'))

class Alumno(db.Model):
    __tablename__ = 'alumno'
    id_alumno = db.Column(db.Integer, primary_key=True)
    nombre_alumno = db.Column(db.String(100))
    # --- NUEVO CAMPO ---
    email_alumno = db.Column(db.String(100)) 
    # -------------------
    pass_alumno = db.Column(db.String(255))
    id_centro_estudios = db.Column(db.Integer, db.ForeignKey('centro_estudios.id_centro_estudios'))
    id_tutor = db.Column(db.Integer, db.ForeignKey('tutor.id_tutor'))
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id_clase'))

# --- OPERATIVA ---

class Informe(db.Model):
    __tablename__ = 'informe'
    id_informe = db.Column(db.Integer, primary_key=True)
    fecha_informe = db.Column(db.DateTime, default=db.func.current_timestamp())
    tipo_bullying = db.Column(db.String(50))
    descripcion = db.Column(db.String(1000))
    id_centro_estudios = db.Column(db.Integer, db.ForeignKey('centro_estudios.id_centro_estudios'))
    id_director = db.Column(db.Integer, db.ForeignKey('directores.id_director'))