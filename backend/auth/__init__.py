from werkzeug.security import check_password_hash
from backend.models import Alumno, Director, Profesor, Tutor

def autenticar_usuario(email, password):
    """
    Busca al usuario por EMAIL en todas las tablas.
    Contraseña universal para pruebas: '1234'
    """
    # 1. Intentar como ALUMNO (Login por EMAIL)
    # Antes buscábamos por 'nombre_alumno', ahora por 'email_alumno'
    alumno = Alumno.query.filter_by(email_alumno=email).first()
    if alumno:
        if alumno.pass_alumno == password or check_password_hash(alumno.pass_alumno, password):
            return "alumno", alumno.nombre_alumno

    # 2. Intentar como DIRECTOR (Login por EMAIL)
    director = Director.query.filter_by(email_director=email).first()
    if director:
        if director.pass_director == password or check_password_hash(director.pass_director, password):
            return "director", director.nombre_director

    # 3. Intentar como PROFESOR (Login por EMAIL - ojo, la columna es mail_profesor)
    profesor = Profesor.query.filter_by(mail_profesor=email).first()
    if profesor:
        if profesor.pass_profesor == password or check_password_hash(profesor.pass_profesor, password):
            return "profesor", profesor.nombre_profesor

    # 4. Intentar como TUTOR (Login por EMAIL)
    tutor = Tutor.query.filter_by(email_tutor=email).first()
    if tutor:
        if tutor.pass_tutor == password or check_password_hash(tutor.pass_tutor, password):
            return "tutor", tutor.nombre_tutor

    return "error", None