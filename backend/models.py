"""
backend/models.py
Modelos de base de datos con SQLAlchemy
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class CentroEducativo(db.Model):
    """Modelo para centros educativos"""
    __tablename__ = 'centros_educativos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    direccion = db.Column(db.String(300))
    telefono = db.Column(db.String(20))
    email_contacto = db.Column(db.String(100))
    codigo_centro = db.Column(db.String(50), unique=True)
    
    # Relaciones
    usuarios = db.relationship('Usuario', backref='centro', lazy=True)
    
    def __repr__(self):
        return f'<Centro {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email_contacto': self.email_contacto,
            'codigo_centro': self.codigo_centro
        }


class Usuario(db.Model):
    """Modelo para usuarios del sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Rol: estudiante, profesor, coordinador, admin
    rol = db.Column(db.String(20), nullable=False, default='estudiante')
    
    # Información adicional
    curso = db.Column(db.String(50))  # Para estudiantes
    departamento = db.Column(db.String(100))  # Para profesores
    
    # Centro educativo
    centro_educativo_id = db.Column(db.Integer, db.ForeignKey('centros_educativos.id'))
    
    # Metadata
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    conversaciones = db.relationship('Conversacion', backref='usuario', lazy=True)
    
    def set_password(self, password):
        """Hashea la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'email': self.email,
            'rol': self.rol,
            'curso': self.curso,
            'departamento': self.departamento,
            'centro_educativo_id': self.centro_educativo_id,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'activo': self.activo
        }


class Conversacion(db.Model):
    """Modelo para conversaciones del chatbot"""
    __tablename__ = 'conversaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Timestamps
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    
    # Estado: activa, finalizada, cancelada
    estado = db.Column(db.String(20), default='activa')
    
    # Metadata en JSON
    metadata_json = db.Column(db.Text)  # Datos adicionales
    
    # Relaciones
    mensajes = db.relationship('Mensaje', backref='conversacion', lazy=True, cascade='all, delete-orphan')
    reporte = db.relationship('Reporte', backref='conversacion', uselist=False, cascade='all, delete-orphan')
    
    def set_metadata(self, data):
        """Guarda metadata como JSON"""
        self.metadata_json = json.dumps(data, ensure_ascii=False)
    
    def get_metadata(self):
        """Recupera metadata desde JSON"""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}
    
    def __repr__(self):
        return f'<Conversacion {self.id} - Usuario {self.usuario_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'estado': self.estado,
            'metadata': self.get_metadata(),
            'num_mensajes': len(self.mensajes) if self.mensajes else 0
        }


class Mensaje(db.Model):
    """Modelo para mensajes de la conversación"""
    __tablename__ = 'mensajes'
    
    id = db.Column(db.Integer, primary_key=True)
    conversacion_id = db.Column(db.Integer, db.ForeignKey('conversaciones.id'), nullable=False)
    
    # Rol: usuario, asistente, sistema
    rol = db.Column(db.String(20), nullable=False)
    
    # Contenido del mensaje
    contenido = db.Column(db.Text, nullable=False)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata (sentiment, entities, etc.)
    metadata_json = db.Column(db.Text)
    
    def set_metadata(self, data):
        """Guarda metadata como JSON"""
        self.metadata_json = json.dumps(data, ensure_ascii=False)
    
    def get_metadata(self):
        """Recupera metadata desde JSON"""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}
    
    def __repr__(self):
        return f'<Mensaje {self.id} - {self.rol}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversacion_id': self.conversacion_id,
            'rol': self.rol,
            'contenido': self.contenido,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metadata': self.get_metadata()
        }


class Reporte(db.Model):
    """Modelo para reportes generados"""
    __tablename__ = 'reportes'
    
    id = db.Column(db.Integer, primary_key=True)
    conversacion_id = db.Column(db.Integer, db.ForeignKey('conversaciones.id'), nullable=False, unique=True)
    
    # Clasificación de gravedad: leve, moderado, grave, critico
    clasificacion_gravedad = db.Column(db.String(20), nullable=False)
    
    # Tipo de bullying detectado
    tipo_bullying = db.Column(db.String(100))  # verbal, físico, ciberbullying, exclusión
    
    # Resumen ejecutivo
    resumen = db.Column(db.Text)
    
    # Informe completo en JSON
    informe_json = db.Column(db.Text, nullable=False)
    
    # Ruta al PDF generado
    pdf_path = db.Column(db.String(500))
    
    # Estado de envío
    enviado = db.Column(db.Boolean, default=False)
    fecha_envio = db.Column(db.DateTime)
    destinatarios = db.Column(db.Text)  # Emails separados por comas
    
    # Timestamp
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_informe(self, data):
        """Guarda informe como JSON"""
        self.informe_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    def get_informe(self):
        """Recupera informe desde JSON"""
        if self.informe_json:
            return json.loads(self.informe_json)
        return {}
    
    def __repr__(self):
        return f'<Reporte {self.id} - {self.clasificacion_gravedad}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversacion_id': self.conversacion_id,
            'clasificacion_gravedad': self.clasificacion_gravedad,
            'tipo_bullying': self.tipo_bullying,
            'resumen': self.resumen,
            'informe': self.get_informe(),
            'pdf_path': self.pdf_path,
            'enviado': self.enviado,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
            'destinatarios': self.destinatarios.split(',') if self.destinatarios else [],
            'fecha_generacion': self.fecha_generacion.isoformat() if self.fecha_generacion else None
        }


def init_db(app):
    """Inicializa la base de datos"""
    db.init_app(app)
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Base de datos inicializada correctamente")


def reset_db(app):
    """Resetea la base de datos (CUIDADO: elimina todos los datos)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("⚠️  Base de datos reseteada")