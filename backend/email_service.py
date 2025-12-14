import os

def enviar_notificacion_protocolo(destinatarios, asunto, cuerpo, ruta_adjunto):
    """
    Simula el envío de un correo electrónico a las autoridades del centro.
    Imprime los detalles en la terminal para verificar que el sistema funciona.
    """
    print("\n" + "="*60)
    print("📧  SERVICIO DE CORREO 'SAY IT' (SIMULACIÓN)")
    print("="*60)
    print(f"📨 PARA:      {', '.join(destinatarios)}")
    print(f"📌 ASUNTO:    {asunto}")
    
    adjunto_nombre = os.path.basename(ruta_adjunto) if ruta_adjunto else "Ninguno"
    print(f"📎 ADJUNTO:   {adjunto_nombre}")
    
    print("-" * 60)
    print("CUERPO DEL MENSAJE:")
    print(cuerpo)
    print("="*60 + "\n")
    
    return True