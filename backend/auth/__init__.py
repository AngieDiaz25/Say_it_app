from werkzeug.security import check_password_hash
from backend.models import Alumno, Director, Profesor, Tutor

def autenticar_usuario(email, password):
    """
    Busca al usuario en todas las tablas (Alumno, Director, Tutor, Profesor).
    Verifica la contraseña contra el campo 'password_hash'.
    """
    
    # 1. Buscar en ALUMNOS
    alumno = Alumno.query.filter_by(email_alumno=email).first()
    if alumno:
        # Nota: En producción usaríamos check_password_hash. 
        # Para la demo, comparamos texto plano porque reset_db.py guardó "1234" tal cual.
        if alumno.password_hash == password:
            return "alumno", alumno.nombre_alumno
    
    # 2. Buscar en DIRECTORES
    director = Director.query.filter_by(email_director=email).first()
    if director:
        if director.password_hash == password:
            return "director", director.nombre_director

    # 3. Buscar en TUTORES
    tutor = Tutor.query.filter_by(email_tutor=email).first()
    if tutor:
        if tutor.password_hash == password:
            return "tutor", tutor.nombre_tutor
            
    # 4. Buscar en PROFESORES
    profesor = Profesor.query.filter_by(email_profesor=email).first()
    if profesor:
        if profesor.password_hash == password:
            return "profesor", profesor.nombre_profesor

    return "error", None