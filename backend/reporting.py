import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generar_pdf_informe(id_informe, datos_ia, historial_chat, nombre_centro):
    # 1. Crear carpeta si no existe
    output_dir = os.path.join(os.getcwd(), "data", "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Ruta del archivo
    filename = f"Informe_{id_informe}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # 3. Generar PDF
    try:
        c = canvas.Canvas(filepath, pagesize=letter)
        y = 750 # Altura inicial
        
        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, f"EXPEDIENTE CONFIDENCIAL #{id_informe}")
        y -= 30
        
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        y -= 20
        c.drawString(50, y, f"Centro: {nombre_centro}")
        y -= 40
        
        # Datos de Riesgo
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "ANÁLISIS DE RIESGO (IA):")
        y -= 20
        
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Rol detectado: {datos_ia.get('rol_informante', '-')}")
        y -= 15
        c.drawString(50, y, f"Tipo incidente: {datos_ia.get('tipo_incidente', '-')}")
        y -= 15
        c.drawString(50, y, f"Nivel gravedad: {datos_ia.get('nivel_gravedad', '-')}")
        y -= 15
        
        # Resumen
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "RESUMEN DE HECHOS:")
        y -= 20
        c.setFont("Helvetica", 10)
        
        resumen = datos_ia.get('resumen_hechos', 'Sin resumen')
        # Cortar texto largo simple para que no se salga
        if len(resumen) > 80: resumen = resumen[:80] + "..."
        c.drawString(50, y, resumen)
        
        c.save()
        return filepath
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return "Error al generar archivo físico"