import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, red, gray, navy
from datetime import datetime

def generar_pdf_informe(id_informe, fecha_reporte, datos_ia, nombre_centro, id_centro, 
                        id_director, nombre_director, 
                        id_docente, nombre_docente, 
                        id_alumno, nombre_alumno):
    """
    Genera un expediente PDF incluyendo NOMBRES e IDs de todos los implicados.
    """
    output_dir = os.path.join(os.getcwd(), "data", "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"Reporte_{id_informe}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    try:
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # --- MARCA DE AGUA ---
        c.saveState()
        c.setFont("Helvetica-Bold", 60)
        c.setFillColor(gray, alpha=0.1)
        c.translate(300, 400)
        c.rotate(45)
        c.drawCentredString(0, 0, "CONFIDENCIAL")
        c.restoreState()
        
        # --- TÍTULO ---
        c.setStrokeColor(navy)
        c.setLineWidth(3)
        c.line(50, height - 50, width - 50, height - 50)
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(navy)
        c.drawString(50, height - 80, f"REPORTE DE INCIDENCIA #{id_informe}")
        
        # --- 1. DATOS DE IDENTIFICACIÓN (Nombres + IDs) ---
        y = height - 120
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "1. IDENTIFICACIÓN Y RESPONSABLES")
        y -= 25
        
        c.setFont("Helvetica", 10)
        # Fila 1: Fecha y Centro
        c.drawString(60, y, f"Fecha: {fecha_reporte}")
        c.drawString(300, y, f"Centro: {nombre_centro} (ID: {id_centro})")
        y -= 20
        
        # Fila 2: Alumno Informante
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "Alumno Informante:")
        c.setFont("Helvetica", 10)
        c.drawString(170, y, f"{nombre_alumno} (ID: {id_alumno})")
        y -= 20
        
        # Fila 3: Director Responsable
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "Director Asignado:")
        c.setFont("Helvetica", 10)
        c.drawString(170, y, f"{nombre_director} (ID: {id_director if id_director else 'N/A'})")
        y -= 20
        
        # Fila 4: Tutor/Docente
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "Tutor/Docente:")
        c.setFont("Helvetica", 10)
        c.drawString(170, y, f"{nombre_docente} (ID: {id_docente if id_docente else 'N/A'})")
        
        # --- 2. CLASIFICACIÓN ---
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "2. CLASIFICACIÓN DEL INCIDENTE")
        y -= 25
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "Tipo de Incidente:")
        c.setFont("Helvetica", 10)
        c.drawString(170, y, str(datos_ia.get('tipo_incidente', 'No especificado')))
        
        y -= 20
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "Nivel de Gravedad:")
        gravedad = datos_ia.get('nivel_gravedad', 'LEVE')
        if gravedad in ['GRAVE', 'MUY GRAVE', 'CRITICO']:
            c.setFillColor(red)
        c.drawString(170, y, gravedad)
        c.setFillColor(black)
        
        # --- 3. HECHOS ---
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "3. RESUMEN DE LOS HECHOS")
        y -= 25
        
        resumen = datos_ia.get('resumen_hechos', 'Sin resumen disponible.')
        
        text_object = c.beginText(60, y)
        text_object.setFont("Helvetica", 10)
        text_object.setTextOrigin(60, y)
        palabras = resumen.split()
        linea_actual = ""
        for palabra in palabras:
            if c.stringWidth(linea_actual + " " + palabra, "Helvetica", 10) < 450:
                linea_actual += " " + palabra
            else:
                text_object.textLine(linea_actual)
                linea_actual = palabra
        text_object.textLine(linea_actual)
        c.drawText(text_object)
        
        # Pie de página
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(gray)
        c.drawCentredString(width/2, 30, "Documento generado automáticamente por el Sistema Say It")
        
        c.save()
        return filepath
        
    except Exception as e:
        print(f"Error PDF: {e}")
        return None