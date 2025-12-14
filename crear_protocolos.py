import os

def crear_documentos():
    folder = "documentos_rag"
    os.makedirs(folder, exist_ok=True)

    # DOCUMENTO 1: Reglamento Disciplinario
    texto_reglamento = """
    REGLAMENTO DE RÉGIMEN INTERNO - TIPIFICACIÓN DE FALTAS

    ARTÍCULO 14. FALTAS GRAVES:
    a) Las agresiones físicas o amenazas.
    b) Las vejaciones o humillaciones públicas o privadas.
    c) La grabación, publicidad o difusión de agresiones o humillaciones (Ciberbullying).

    ARTÍCULO 15. SANCIONES:
    - Las faltas graves conllevarán la apertura de expediente disciplinario.
    - Medida cautelar: Suspensión del derecho de asistencia al centro de 3 a 15 días.
    """

    # DOCUMENTO 2: Procedimiento de Denuncia
    texto_procedimiento = """
    PROCEDIMIENTO DE APERTURA DE EXPEDIENTE

    1. El alumno informante debe facilitar: Nombres de implicados, fechas y descripción fáctica de los hechos.
    2. El sistema 'Say It' registrará la denuncia y generará un número de expediente.
    3. El Director recibirá el informe en un plazo máximo de 24 horas.
    4. Se garantiza la confidencialidad de los datos según la LOPD.
    """

    with open(f"{folder}/reglamento.txt", "w", encoding="utf-8") as f:
        f.write(texto_reglamento)

    with open(f"{folder}/procedimiento.txt", "w", encoding="utf-8") as f:
        f.write(texto_procedimiento)

    print(f"✅ Protocolos normativos generados en '{folder}'.")

if __name__ == "__main__":
    crear_documentos()