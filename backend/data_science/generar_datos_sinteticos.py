"""
backend/data_science/generar_datos_sinteticos.py
Genera datos sintéticos realistas para testing del sistema
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask
from faker import Faker
from datetime import datetime, timedelta
import random
import json

# Importar modelos
from backend.models import db, CentroEducativo, Usuario, Conversacion, Mensaje, Reporte

# Inicializar Faker en español
fake = Faker('es_ES')


def crear_app_temp():
    """Crea una app Flask temporal para generar datos"""
    app = Flask(__name__)
    
    # Construir ruta absoluta a la base de datos
    basedir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.join(basedir, '..', '..')
    db_path = os.path.join(project_root, 'data', 'bullying.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return app


def generar_centros_educativos():
    """Genera 5 centros educativos ficticios"""
    
    centros = [
        {
            'nombre': 'IES Miguel de Cervantes',
            'direccion': 'Calle de la Constitución, 45, Madrid',
            'telefono': '912345678',
            'email_contacto': 'direccion@iescervantes.edu.es',
            'codigo_centro': 'IES001'
        },
        {
            'nombre': 'Colegio Santa Teresa',
            'direccion': 'Av. de la Libertad, 123, Barcelona',
            'telefono': '934567890',
            'email_contacto': 'info@santateresa.edu.es',
            'codigo_centro': 'COL002'
        },
        {
            'nombre': 'IES Valle Inclán',
            'direccion': 'Plaza Mayor, 8, Valencia',
            'telefono': '963456789',
            'email_contacto': 'secretaria@iesvalle.edu.es',
            'codigo_centro': 'IES003'
        },
        {
            'nombre': 'Colegio San José',
            'direccion': 'Calle Real, 56, Sevilla',
            'telefono': '954123456',
            'email_contacto': 'direccion@sanjose.edu.es',
            'codigo_centro': 'COL004'
        },
        {
            'nombre': 'IES Rafael Alberti',
            'direccion': 'Av. Principal, 234, Málaga',
            'telefono': '952678901',
            'email_contacto': 'info@iesalberti.edu.es',
            'codigo_centro': 'IES005'
        }
    ]
    
    centros_db = []
    for centro_data in centros:
        centro = CentroEducativo(**centro_data)
        db.session.add(centro)
        centros_db.append(centro)
    
    db.session.commit()
    print(f"✓ Creados {len(centros_db)} centros educativos")
    return centros_db


def generar_usuarios(centros):
    """Genera usuarios: estudiantes, profesores y coordinadores"""
    
    usuarios = []
    
    # Por cada centro
    for centro in centros:
        # 1 Coordinador por centro
        coordinador = Usuario(
            nombre=fake.first_name(),
            apellidos=fake.last_name(),
            email=f"coordinador.{centro.codigo_centro.lower()}@{centro.codigo_centro.lower()}.edu.es",
            rol='coordinador',
            departamento='Dirección',
            centro_educativo_id=centro.id
        )
        coordinador.set_password('Coordinador123!')
        db.session.add(coordinador)
        usuarios.append(coordinador)
        
        # 3 Profesores por centro
        for i in range(3):
            profesor = Usuario(
                nombre=fake.first_name(),
                apellidos=fake.last_name(),
                email=fake.email(),
                rol='profesor',
                departamento=random.choice(['Matemáticas', 'Lengua', 'Ciencias', 'Historia', 'Inglés']),
                centro_educativo_id=centro.id
            )
            profesor.set_password('Profesor123!')
            db.session.add(profesor)
            usuarios.append(profesor)
        
        # 6 Estudiantes por centro
        cursos = ['1º ESO', '2º ESO', '3º ESO', '4º ESO', '1º Bach', '2º Bach']
        for curso in cursos:
            estudiante = Usuario(
                nombre=fake.first_name(),
                apellidos=fake.last_name(),
                email=fake.email(),
                rol='estudiante',
                curso=curso,
                centro_educativo_id=centro.id,
                fecha_registro=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            estudiante.set_password('Estudiante123!')
            db.session.add(estudiante)
            usuarios.append(estudiante)
    
    # 1 Admin global
    admin = Usuario(
        nombre='Admin',
        apellidos='Sistema',
        email='admin@sayitapp.com',
        rol='admin',
        centro_educativo_id=centros[0].id
    )
    admin.set_password('Admin123!')
    db.session.add(admin)
    usuarios.append(admin)
    
    db.session.commit()
    print(f"✓ Creados {len(usuarios)} usuarios")
    return usuarios


def generar_conversaciones_realistas(usuarios):
    """Genera conversaciones realistas de casos de bullying"""
    
    # Plantillas de conversaciones por tipo de bullying
    conversaciones_tipo = {
        'ciberbullying': [
            {
                'mensajes': [
                    ('usuario', 'Hola... necesito hablar con alguien'),
                    ('asistente', 'Hola, estoy aquí para escucharte en un espacio seguro. ¿Qué está pasando?'),
                    ('usuario', 'Es que en el grupo de WhatsApp de clase están compartiendo fotos mías editadas'),
                    ('asistente', 'Entiendo que esto debe ser muy difícil para ti. ¿Desde cuándo está ocurriendo esto?'),
                    ('usuario', 'Desde hace como dos semanas... cada día suben algo nuevo'),
                    ('asistente', '¿Puedes contarme quiénes están involucrados en esto?'),
                    ('usuario', 'Son varios de mi clase, pero quien más lo hace es Carlos y su grupo de amigos'),
                    ('asistente', '¿Has podido hablar con alguien sobre esto? ¿Tus padres o algún profesor saben lo que está pasando?'),
                    ('usuario', 'No, me da vergüenza... y tengo miedo de que empeore si digo algo'),
                    ('asistente', 'Es completamente normal sentir miedo, pero es importante que sepas que no estás solo/a y que hay personas que pueden ayudarte. ¿Cómo te está afectando esta situación?'),
                    ('usuario', 'Ya no quiero ir al colegio... no puedo dormir bien pensando en qué van a subir mañana'),
                ],
                'gravedad': 'grave',
                'tipo': 'ciberbullying'
            }
        ],
        'exclusion': [
            {
                'mensajes': [
                    ('usuario', 'Necesito ayuda'),
                    ('asistente', 'Hola, cuéntame qué te está pasando. Estoy aquí para escucharte.'),
                    ('usuario', 'Nadie en mi clase me habla... me ignoran completamente'),
                    ('asistente', 'Lamento mucho que estés pasando por esto. ¿Desde cuándo empezó esta situación?'),
                    ('usuario', 'Desde principio de curso, cuando llegué nuevo al instituto'),
                    ('asistente', '¿Hay algún grupo o personas específicas que lideren esta exclusión?'),
                    ('usuario', 'Sí, hay un grupo de chicas que son como las "populares" y si ellas no te hablan, nadie lo hace'),
                    ('asistente', '¿Has intentado hablar con alguna de ellas o con algún profesor sobre lo que sientes?'),
                    ('usuario', 'Intenté hablar con una compañera pero me ignoró... y con los profesores no me atrevo'),
                    ('asistente', '¿Cómo está afectando esta situación a tu día a día en el colegio?'),
                    ('usuario', 'Como solo en los recreos, no tengo con quien hacer trabajos en grupo... me siento muy solo'),
                ],
                'gravedad': 'moderado',
                'tipo': 'exclusión social'
            }
        ],
        'verbal': [
            {
                'mensajes': [
                    ('usuario', 'Hola'),
                    ('asistente', 'Hola, ¿en qué puedo ayudarte hoy?'),
                    ('usuario', 'No sé si esto cuenta como bullying pero me están insultando mucho'),
                    ('asistente', 'Por supuesto que cuenta. Los insultos son una forma de acoso. ¿Puedes contarme más sobre lo que está pasando?'),
                    ('usuario', 'Cada día cuando llego a clase, un grupo me dice cosas feas sobre mi peso'),
                    ('asistente', 'Eso no está bien y no deberías tener que soportarlo. ¿Quiénes son las personas que te dicen estas cosas?'),
                    ('usuario', 'Son Jorge, Miguel y a veces Pablo... están en mi clase'),
                    ('asistente', '¿Desde cuándo viene ocurriendo esto?'),
                    ('usuario', 'Desde hace unos tres meses... al principio pensé que eran bromas pero no paran'),
                    ('asistente', '¿Has podido hablar con algún adulto sobre esto? ¿Algún profesor o tus padres?'),
                    ('usuario', 'Mis padres lo saben pero me dijeron que los ignore... pero no funciona'),
                    ('asistente', '¿Cómo te hace sentir esta situación?'),
                    ('usuario', 'Me siento muy mal... cada noche antes de dormir pienso en qué me van a decir mañana'),
                ],
                'gravedad': 'grave',
                'tipo': 'acoso verbal'
            }
        ],
        'fisico': [
            {
                'mensajes': [
                    ('usuario', 'Necesito reportar algo grave'),
                    ('asistente', 'Estoy aquí para ayudarte. Cuéntame qué está pasando.'),
                    ('usuario', 'Ayer me empujaron en el pasillo y me caí... me hice daño en la rodilla'),
                    ('asistente', 'Eso es muy serio. ¿Quién te empujó?'),
                    ('usuario', 'Fue David, lo hace seguido cuando no hay profesores cerca'),
                    ('asistente', '¿Cuántas veces ha pasado esto?'),
                    ('usuario', 'Esta semana es la tercera vez... la semana pasada también me quitó el bocadillo'),
                    ('asistente', '¿Algún profesor o adulto sabe lo que está ocurriendo?'),
                    ('usuario', 'No... tengo miedo de que si digo algo me haga algo peor'),
                    ('asistente', '¿Tus padres saben lo que está pasando?'),
                    ('usuario', 'No, no les he dicho nada todavía'),
                    ('asistente', 'Es muy importante que un adulto sepa lo que está pasando. ¿Te gustaría que te ayudáramos a hablar con alguien de confianza?'),
                    ('usuario', 'Sí... creo que sí necesito ayuda'),
                ],
                'gravedad': 'critico',
                'tipo': 'acoso físico'
            }
        ],
        'leve': [
            {
                'mensajes': [
                    ('usuario', 'Hola, no sé si esto es importante'),
                    ('asistente', 'Hola, todo lo que te preocupa es importante. Cuéntame.'),
                    ('usuario', 'Es que un compañero me molesta en clase'),
                    ('asistente', '¿Qué tipo de cosas hace que te molestan?'),
                    ('usuario', 'Me tira papelitos y se ríe cuando me equivoco al hablar'),
                    ('asistente', '¿Esto pasa frecuentemente?'),
                    ('usuario', 'Sí, como dos o tres veces por semana en clase de mates'),
                    ('asistente', '¿Has intentado hablar con esta persona o con el profesor de matemáticas?'),
                    ('usuario', 'No, porque tampoco es tan grave... ¿verdad?'),
                    ('asistente', 'Cualquier comportamiento que te haga sentir incómodo es importante. ¿Te gustaría que te ayudáramos a manejar esta situación?'),
                    ('usuario', 'Sí, estaría bien saber cómo hablar con él'),
                ],
                'gravedad': 'leve',
                'tipo': 'molestias menores'
            }
        ]
    }
    
    conversaciones_creadas = []
    estudiantes = [u for u in usuarios if u.rol == 'estudiante']
    
    # Generar 30-40 conversaciones
    num_conversaciones = random.randint(30, 40)
    
    for _ in range(num_conversaciones):
        estudiante = random.choice(estudiantes)
        tipo_bullying = random.choice(list(conversaciones_tipo.keys()))
        plantilla = random.choice(conversaciones_tipo[tipo_bullying])
        
        # Crear conversación
        fecha_inicio = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        conversacion = Conversacion(
            usuario_id=estudiante.id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_inicio + timedelta(minutes=random.randint(10, 45)),
            estado='finalizada'
        )
        
        metadata = {
            'ip_address': fake.ipv4(),
            'user_agent': 'Mozilla/5.0',
            'duracion_minutos': random.randint(10, 45)
        }
        conversacion.set_metadata(metadata)
        
        db.session.add(conversacion)
        db.session.flush()  # Para obtener el ID
        
        # Crear mensajes
        for i, (rol, contenido) in enumerate(plantilla['mensajes']):
            mensaje = Mensaje(
                conversacion_id=conversacion.id,
                rol=rol,
                contenido=contenido,
                timestamp=fecha_inicio + timedelta(minutes=i*2)
            )
            db.session.add(mensaje)
        
        # Crear reporte
        reporte = Reporte(
            conversacion_id=conversacion.id,
            clasificacion_gravedad=plantilla['gravedad'],
            tipo_bullying=plantilla['tipo'],
            resumen=f"Caso de {plantilla['tipo']} reportado por estudiante de {estudiante.curso}"
        )
        
        informe_data = {
            'estudiante': {
                'nombre_anonimo': 'Estudiante ' + str(estudiante.id),
                'curso': estudiante.curso
            },
            'incidente': {
                'tipo': plantilla['tipo'],
                'gravedad': plantilla['gravedad'],
                'fecha_reporte': fecha_inicio.isoformat()
            },
            'resumen': f"Se reporta un caso de {plantilla['tipo']} con nivel de gravedad {plantilla['gravedad']}."
        }
        reporte.set_informe(informe_data)
        
        db.session.add(reporte)
        conversaciones_creadas.append(conversacion)
    
    db.session.commit()
    print(f"✓ Creadas {len(conversaciones_creadas)} conversaciones con mensajes y reportes")
    return conversaciones_creadas


def main():
    """Función principal"""
    print("=" * 60)
    print("  GENERADOR DE DATOS SINTÉTICOS")
    print("  Sistema Anti-Bullying")
    print("=" * 60)
    print()
    
    # Crear directorio data si no existe
    os.makedirs('data', exist_ok=True)
    
    # Crear app y contexto
    app = crear_app_temp()
    
    with app.app_context():
        # Limpiar base de datos existente
        db.drop_all()
        db.create_all()
        print("✓ Base de datos inicializada")
        print()
        
        # Generar datos
        print("Generando datos sintéticos...")
        print()
        
        centros = generar_centros_educativos()
        usuarios = generar_usuarios(centros)
        conversaciones = generar_conversaciones_realistas(usuarios)
        
        print()
        print("=" * 60)
        print("✅ DATOS GENERADOS EXITOSAMENTE")
        print("=" * 60)
        print()
        print("📊 Resumen:")
        print(f"  • Centros educativos: {len(centros)}")
        print(f"  • Usuarios totales: {len(usuarios)}")
        print(f"    - Estudiantes: {len([u for u in usuarios if u.rol == 'estudiante'])}")
        print(f"    - Profesores: {len([u for u in usuarios if u.rol == 'profesor'])}")
        print(f"    - Coordinadores: {len([u for u in usuarios if u.rol == 'coordinador'])}")
        print(f"    - Administradores: {len([u for u in usuarios if u.rol == 'admin'])}")
        print(f"  • Conversaciones: {len(conversaciones)}")
        print()
        print("🔐 Credenciales de prueba:")
        print("  • Admin: admin@sayitapp.com / Admin123!")
        print("  • Coordinador: coordinador.ies001@ies001.edu.es / Coordinador123!")
        print("  • Cualquier estudiante: usar emails generados / Estudiante123!")
        print()
        print("📁 Base de datos guardada en: data/bullying.db")
        print()


if __name__ == "__main__":
    main()