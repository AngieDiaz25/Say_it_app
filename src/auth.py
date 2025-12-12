import bcrypt

def hash_password(password: str) -> str:
    """
    Toma una contraseña en texto plano y devuelve su hash seguro.
    Usamos bcrypt con 'salt' automático para evitar ataques de Rainbow Tables.
    """
    # Convertimos la contraseña a bytes
    password_bytes = password.encode('utf-8')
    # Generamos el salt y el hash
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Devolvemos como string para guardar en JSON/SQL
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara una contraseña introducida por el usuario con el hash guardado en la DB.
    Devuelve True si coinciden, False si no.
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Checkpw hace la comparación segura (resistente a ataques de tiempo)
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"Error verificando contraseña: {e}")
        return False

# --- Bloque de Prueba (Solo se ejecuta si corres este archivo directamente) ---
if __name__ == "__main__":
    print("--- Test de Seguridad ---")
    pass_real = "mi_secreto_super_seguro"
    
    # 1. Simular registro
    hash_generado = hash_password(pass_real)
    print(f"Contraseña: {pass_real}")
    print(f"Hash Guardado en DB: {hash_generado}")
    
    # 2. Simular Login correcto
    login_ok = verify_password("mi_secreto_super_seguro", hash_generado)
    print(f"Login Correcto: {login_ok}") # Debería ser True
    
    # 3. Simular Hackeo (Login incorrecto)
    login_fail = verify_password("123456", hash_generado)
    print(f"Intento Hackeo: {login_fail}") # Debería ser False