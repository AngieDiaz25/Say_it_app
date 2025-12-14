import bcrypt
from backend.models import Director, Alumno, Tutor, Profesor

def hash_password(password: str) -> str:
    """
    Convierte una contraseña normal en un hash seguro para guardarla en la BD.
    """
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    return hash.decode('utf-8')

def check_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara la contraseña que escribe el usuario con el hash guardado.
    """
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

def autenticar_usuario(username, password):
    """
    Busca al usuario en las 4 tablas posibles y devuelve su rol y nombre real.
    """
    # 1. DIRECTOR (Panel de Gestión)
    # Busca por email
    director = Director.query.filter_by(email_director=username).first()
    if director and check_password(password, director.pass_director):
        return "director", director.nombre_director

    # 2. PROFESOR (Panel Docente)
    # Busca por email
    profesor = Profesor.query.filter_by(mail_profesor=username).first()
    if profesor and check_password(password, profesor.pass_profesor):
        return "profesor", profesor.nombre_profesor

    # 3. TUTOR / PADRE (Portal Familias)
    # Busca por email
    tutor = Tutor.query.filter_by(email_tutor=username).first()
    if tutor and check_password(password, tutor.pass_tutor):
        return "tutor", tutor.nombre_tutor

    # 4. ALUMNO (Chat de Denuncia)
    # Busca por nombre (o email si cambiaste el generador, aquí usamos nombre por defecto)
    alumno = Alumno.query.filter_by(nombre_alumno=username).first()
    if alumno and check_password(password, alumno.pass_alumno):
        return "alumno", alumno.nombre_alumno

    # Si no encuentra nada:
    return "error", "Usuario no encontrado"