import bcrypt

def hash_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano a un hash seguro usando Bcrypt.
    """
    # Convertimos la password a bytes
    bytes = password.encode('utf-8')
    # Generamos la sal (salt) y el hash
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    # Devolvemos como string para guardar en la BD
    return hash.decode('utf-8')

def check_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña coincide con el hash.
    """
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)