"""
Say It App - Sistema Anti-Bullying
Frontend Gradio Profesional
"""

import gradio as gr
import os
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from io import BytesIO

from backend.models import db, Alumno, CentroEstudios, Informe, Director, Tutor, Profesor
from backend.auth import autenticar_usuario
from backend.agents import responder_alumno, generar_reporte_riesgo

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
app = Flask(__name__)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(base_dir, 'bullying.db')
reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'reports'))

# Crear carpeta de reportes si no existe
os.makedirs(reports_dir, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- 2. CSS PERSONALIZADO ---
custom_css = """
/* ==============================
   Say It - Custom CSS Theme
   ============================== */

/* Variables de color */
:root {
    --primary-color: #4F46E5;
    --primary-dark: #3730A3;
    --primary-light: #818CF8;
    --secondary-color: #F97316;
    --secondary-light: #FB923C;
    --success-color: #10B981;
    --warning-color: #F59E0B;
    --danger-color: #EF4444;
    --background-dark: #0F172A;
    --background-card: rgba(30, 41, 59, 0.8);
    --text-primary: #F1F5F9;
    --text-secondary: #94A3B8;
    --border-color: rgba(148, 163, 184, 0.2);
}

/* Fondo general */
.gradio-container {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%) !important;
    min-height: 100vh;
}

/* Header principal */
.header-container {
    background: linear-gradient(90deg, var(--primary-color), var(--primary-dark));
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(79, 70, 229, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.header-title {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    color: white !important;
    margin: 0 !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.header-subtitle {
    color: rgba(255, 255, 255, 0.8) !important;
    font-size: 1.1rem !important;
    margin-top: 8px !important;
}

/* Cards / Paneles */
.panel-card {
    background: var(--background-card) !important;
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
}

/* Login Card */
.login-card {
    max-width: 420px;
    margin: 40px auto;
    background: var(--background-card) !important;
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-color) !important;
    border-radius: 20px !important;
    padding: 40px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.login-title {
    text-align: center;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin-bottom: 8px !important;
}

.login-subtitle {
    text-align: center;
    color: var(--text-secondary) !important;
    margin-bottom: 24px !important;
}

/* Botones */
.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    color: white !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4) !important;
}

.btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
}

.btn-danger {
    background: linear-gradient(135deg, var(--danger-color), #DC2626) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
}

.btn-success {
    background: linear-gradient(135deg, var(--success-color), #059669) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

.btn-secondary {
    background: var(--background-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

/* Inputs */
.input-field input, .input-field textarea {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease !important;
}

.input-field input:focus, .input-field textarea:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
}

/* Stats Cards */
.stat-card {
    background: var(--background-card);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    border: 1px solid var(--border-color);
}

.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary-light);
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 4px;
}

/* Tabla */
.dataframe-container {
    background: var(--background-card) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border-color) !important;
    overflow: hidden;
}

/* Chatbot */
.chatbot-container {
    border-radius: 16px !important;
    background: var(--background-card) !important;
    border: 1px solid var(--border-color) !important;
}

/* Mensajes */
.message-success {
    background: rgba(16, 185, 129, 0.1) !important;
    border: 1px solid var(--success-color) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    color: var(--success-color) !important;
}

.message-error {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 1px solid var(--danger-color) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    color: var(--danger-color) !important;
}

/* Badges de estado */
.badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-pending {
    background: rgba(245, 158, 11, 0.2);
    color: var(--warning-color);
}

.badge-progress {
    background: rgba(79, 70, 229, 0.2);
    color: var(--primary-light);
}

.badge-resolved {
    background: rgba(16, 185, 129, 0.2);
    color: var(--success-color);
}

/* Animaciones */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.3s ease-out;
}

/* Welcome message */
.welcome-box {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(129, 140, 248, 0.1));
    border: 1px solid rgba(79, 70, 229, 0.3);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
}

/* Responsive */
@media (max-width: 768px) {
    .header-title {
        font-size: 1.8rem !important;
    }
    .login-card {
        margin: 20px;
        padding: 24px !important;
    }
}
"""

# --- 3. LÓGICA DE NEGOCIO (BACKEND) ---

def procesar_login(username, password):
    """Autentica usuario y devuelve rol, mensaje y nombre"""
    with app.app_context():
        rol, nombre = autenticar_usuario(username, password)
        if rol == "error":
            return rol, "❌ Credenciales incorrectas. Verifica tu usuario y contraseña.", ""
        
        mensajes = {
            "alumno": f"👋 Hola {nombre}. Este es un espacio seguro para ti.",
            "director": f"📊 Panel de Dirección. Bienvenido/a {nombre}.",
            "profesor": f"👨‍🏫 Panel Docente. Hola {nombre}.",
            "tutor": f"🏠 Portal Familiar. Bienvenido/a {nombre}."
        }
        return rol, mensajes.get(rol, "Bienvenido"), nombre


def guardar_informe_bd(historial_chat, usuario_informante):
    """Guarda el informe en la base de datos"""
    if not historial_chat:
        return "⚠️ El formulario está vacío. Por favor, responde a las preguntas del agente primero."

    # Analizar chat
    datos = generar_reporte_riesgo(historial_chat)
    rol_informante = datos.get("rol_informante", "TESTIGO")
    victima = datos.get("nombre_victima", "No especificado")
    agresores = datos.get("nombre_agresores", "No especificado")
    resumen = datos.get("resumen_hechos", "Sin detalles")
    gravedad = datos.get("nivel_gravedad", "REVISAR")
    tipo = datos.get("tipo_incidente", "Otro")

    with app.app_context():
        informante = Alumno.query.filter_by(nombre_alumno=usuario_informante).first()
        if informante:
            director = Director.query.join(CentroEstudios).filter(
                CentroEstudios.id_centro_estudios == informante.id_centro_estudios
            ).first()
            id_dir = director.id_director if director else None
            
            descripcion_oficial = f"[{rol_informante}] VÍCTIMA: {victima} | AGRESORES: {agresores} | HECHOS: {resumen}"
            
            nuevo_informe = Informe(
                tipo_bullying=tipo,
                descripcion=descripcion_oficial,
                estado="Pendiente",
                id_centro_estudios=informante.id_centro_estudios,
                id_director=id_dir
            )
            db.session.add(nuevo_informe)
            db.session.commit()
            
            return f"""✅ INFORME REGISTRADO CORRECTAMENTE

📋 **Detalles del registro:**
- **Rol:** {rol_informante}
- **Gravedad detectada:** {gravedad}
- **Tipo:** {tipo}

El centro educativo ha sido notificado y revisará tu caso lo antes posible.
Gracias por tu valentía al reportar esta situación. 💪"""
        else:
            return "❌ Error: No se pudo verificar tu identidad. Por favor, contacta con administración."


def obtener_estadisticas():
    """Obtiene estadísticas para el dashboard"""
    with app.app_context():
        total = Informe.query.count()
        pendientes = Informe.query.filter_by(estado="Pendiente").count()
        en_proceso = Informe.query.filter_by(estado="En Proceso").count()
        resueltos = Informe.query.filter_by(estado="Resuelto").count()
        
        # Contar por gravedad (buscando en descripción)
        graves = Informe.query.filter(Informe.descripcion.contains("GRAVE")).count()
        
        return total, pendientes, en_proceso, resueltos, graves


def obtener_datos_dashboard(fecha_desde=None, fecha_hasta=None, tipo_filtro=None, estado_filtro=None):
    """Obtiene informes con filtros opcionales"""
    with app.app_context():
        query = Informe.query.order_by(Informe.fecha_informe.desc())
        
        # Aplicar filtros
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d")
                query = query.filter(Informe.fecha_informe >= fecha_desde_dt)
            except:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(Informe.fecha_informe < fecha_hasta_dt)
            except:
                pass
        
        if tipo_filtro and tipo_filtro != "Todos":
            query = query.filter(Informe.tipo_bullying == tipo_filtro)
        
        if estado_filtro and estado_filtro != "Todos":
            query = query.filter(Informe.estado == estado_filtro)
        
        informes = query.all()
        
        if not informes:
            return pd.DataFrame(columns=["ID", "Fecha", "Tipo", "Estado", "Descripción"])
        
        data = [
            [
                i.id_informe,
                i.fecha_informe.strftime("%Y-%m-%d %H:%M"),
                i.tipo_bullying or "Sin clasificar",
                i.estado or "Pendiente",
                i.descripcion[:100] + "..." if len(i.descripcion) > 100 else i.descripcion
            ]
            for i in informes
        ]
        return pd.DataFrame(data, columns=["ID", "Fecha", "Tipo", "Estado", "Descripción"])


def cambiar_estado_informe(id_informe, nuevo_estado):
    """Cambia el estado de un informe"""
    if not id_informe:
        return "⚠️ Por favor, introduce el ID del informe."
    
    try:
        id_int = int(id_informe)
    except:
        return "❌ El ID debe ser un número."
    
    with app.app_context():
        informe = Informe.query.get(id_int)
        if not informe:
            return f"❌ No se encontró el informe con ID {id_int}."
        
        informe.estado = nuevo_estado
        db.session.commit()
        return f"✅ Informe #{id_int} actualizado a: **{nuevo_estado}**"


def exportar_excel(fecha_desde, fecha_hasta, tipo_filtro, estado_filtro):
    """Exporta los informes filtrados a Excel"""
    df = obtener_datos_dashboard(fecha_desde, fecha_hasta, tipo_filtro, estado_filtro)
    
    if df.empty:
        return None, "⚠️ No hay datos para exportar."
    
    filename = f"informes_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.xlsx"
    filepath = os.path.join(reports_dir, filename)
    
    df.to_excel(filepath, index=False, engine='openpyxl')
    
    return filepath, f"✅ Archivo exportado: {filename}"


def exportar_pdf(fecha_desde, fecha_hasta, tipo_filtro, estado_filtro):
    """Exporta los informes filtrados a PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    
    df = obtener_datos_dashboard(fecha_desde, fecha_hasta, tipo_filtro, estado_filtro)
    
    if df.empty:
        return None, "⚠️ No hay datos para exportar."
    
    filename = f"informes_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=landscape(A4), 
                            leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=20
    )
    elements.append(Paragraph("📊 Say It - Informe de Incidencias", title_style))
    elements.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Tabla
    table_data = [df.columns.tolist()] + df.values.tolist()
    
    # Ajustar anchos de columna
    col_widths = [1.5*cm, 3.5*cm, 3*cm, 2.5*cm, 15*cm]
    
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1E293B')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return filepath, f"✅ PDF exportado: {filename}"


def obtener_info_tutor(usuario_tutor):
    """Obtiene información para el tutor"""
    return """### 📚 Estado de Convivencia

✅ **No hay incidencias activas** relacionadas con su hijo/a.

Si desea más información o tiene alguna preocupación, puede contactar con el centro educativo a través de los canales oficiales.

---

💡 **Recursos disponibles:**
- Guía para familias sobre prevención del bullying
- Línea de atención al menor: 116 111
- Contacto con el tutor/a de su hijo/a"""


def obtener_tipos_bullying():
    """Obtiene los tipos de bullying únicos de la BD"""
    with app.app_context():
        tipos = db.session.query(Informe.tipo_bullying).distinct().all()
        tipos_lista = ["Todos"] + [t[0] for t in tipos if t[0]]
        return tipos_lista


# --- 4. INTERFAZ GRÁFICA (FRONTEND) ---

tema = gr.themes.Base(
    primary_hue=gr.themes.colors.indigo,
    secondary_hue=gr.themes.colors.orange,
    neutral_hue=gr.themes.colors.slate,
    font=gr.themes.GoogleFont("Inter"),
).set(
    body_background_fill="*neutral_950",
    body_background_fill_dark="*neutral_950",
    block_background_fill="*neutral_900",
    block_background_fill_dark="*neutral_900",
    border_color_primary="*neutral_700",
    border_color_primary_dark="*neutral_700",
)

with gr.Blocks(theme=tema, css=custom_css, title="Say It - App Anti-Bullying") as demo:

    with gr.Row(elem_classes="logo-container"):
        gr.Image(
            value="assets/logo.jpeg",
            show_label=False,
            interactive=False,
            height=120
        )

    
    # Estados
    estado_rol = gr.State("")
    estado_usuario = gr.State("")
    
    # ========== HEADER ==========
    with gr.Column(elem_classes="header-container"):
        gr.Markdown("# 🛡️ Say It", elem_classes="header-title")
        gr.Markdown("Canal Seguro de Convivencia Escolar", elem_classes="header-subtitle")
    
    # ========== VISTA LOGIN ==========
    with gr.Group(visible=True, elem_classes="login-card") as login_view:
        gr.Markdown("### 🔐 Acceso Seguro", elem_classes="login-title")
        gr.Markdown("Introduce tus credenciales para acceder", elem_classes="login-subtitle")
        
        user_input = gr.Textbox(
            label="Usuario",
            placeholder="Tu nombre de usuario o email",
            max_length=1000,
            elem_classes="input-field"
        )
        pass_input = gr.Textbox(
            label="Contraseña",
            type="password",
            placeholder="••••••••",
            max_length=1000,
            elem_classes="input-field"
        )
        login_btn = gr.Button("🚀 Iniciar Sesión", variant="primary", elem_classes="btn-primary")
        login_msg = gr.Markdown("")
    
    # ========== VISTA ALUMNO ==========
    with gr.Group(visible=False, elem_classes="panel-card fade-in") as alumno_view:
        welcome_alumno = gr.Markdown("", elem_classes="welcome-box")
        
        gr.Markdown("""### 💬 Cuéntanos lo que pasó


Este es un espacio seguro y confidencial. Un asistente te guiará para recopilar la información necesaria.

**Recuerda:**
- 🔒 Tu identidad está protegida
- 📝 Indica si eres la víctima o un testigo
- ✅ Al finalizar, pulsa el botón rojo para enviar el informe
        """)
        
        chatbot_alumno = gr.Chatbot(
            height=380,
            elem_classes="chatbot-container",
            show_label=False
        )
        
        with gr.Row():
            txt_mensaje = gr.Textbox(
                placeholder="Escribe aquí lo que quieras contar...",
                show_label=False,
                scale=5,
                max_length=1000,
                elem_classes="input-field"
            )
            btn_enviar_msg = gr.Button("Enviar 📨", variant="primary", scale=1)
        
        gr.Markdown("---")
        
        with gr.Row():
            btn_enviar_informe = gr.Button(
                "📁 REGISTRAR INFORME OFICIAL",
                variant="stop",
                elem_classes="btn-danger",
                scale=2
            )
            btn_logout_alumno = gr.Button("🚪 Cerrar Sesión", elem_classes="btn-secondary", scale=1)
        
        resultado_envio = gr.Markdown("", elem_classes="message-success")
    
    # ========== VISTA PROFESOR/DIRECTOR ==========
    with gr.Group(visible=False, elem_classes="panel-card fade-in") as profesor_view:
        welcome_profesor = gr.Markdown("", elem_classes="welcome-box")
        
        gr.Markdown("### 📊 Dashboard de Gestión")
        
        # Estadísticas
        with gr.Row():
            with gr.Column(scale=1):
                stat_total = gr.Markdown("", elem_classes="stat-card")
            with gr.Column(scale=1):
                stat_pendientes = gr.Markdown("", elem_classes="stat-card")
            with gr.Column(scale=1):
                stat_proceso = gr.Markdown("", elem_classes="stat-card")
            with gr.Column(scale=1):
                stat_resueltos = gr.Markdown("", elem_classes="stat-card")
        
        gr.Markdown("---")
        
        # Filtros
        gr.Markdown("#### 🔍 Filtros")
        with gr.Row():
            filtro_fecha_desde = gr.Textbox(label="Desde (YYYY-MM-DD)", placeholder="2024-01-01", max_length=1000)
            filtro_fecha_hasta = gr.Textbox(label="Hasta (YYYY-MM-DD)", placeholder="2024-12-31", max_length=1000)
            filtro_tipo = gr.Dropdown(
                label="Tipo de Incidente",
                choices=["Todos", "Físico", "Verbal", "Ciberacoso", "Exclusión", "Otro"],
                value="Todos"
            )
            filtro_estado = gr.Dropdown(
                label="Estado",
                choices=["Todos", "Pendiente", "En Proceso", "Resuelto"],
                value="Todos"
            )
        
        with gr.Row():
            btn_filtrar = gr.Button("🔍 Aplicar Filtros", variant="primary", elem_classes="btn-primary")
            btn_refresh = gr.Button("🔄 Actualizar", elem_classes="btn-secondary")
        
        # Tabla de informes
        tabla_informes = gr.Dataframe(
            label="📋 Informes Registrados",
            headers=["ID", "Fecha", "Tipo", "Estado", "Descripción"],
            interactive=False,
            wrap=True,
            elem_classes="dataframe-container"
        )
        
        gr.Markdown("---")
        
        # Cambiar estado
        gr.Markdown("#### ✏️ Cambiar Estado de Informe")
        with gr.Row():
            input_id_informe = gr.Textbox(label="ID del Informe", placeholder="Ej: 5", max_length=1000)
            select_nuevo_estado = gr.Dropdown(
                label="Nuevo Estado",
                choices=["Pendiente", "En Proceso", "Resuelto"],
                value="En Proceso"
            )
            btn_cambiar_estado = gr.Button("💾 Actualizar Estado", variant="primary", elem_classes="btn-success")
        
        resultado_cambio = gr.Markdown("")
        
        gr.Markdown("---")
        
        # Exportar
        gr.Markdown("#### 📥 Exportar Datos")
        with gr.Row():
            btn_export_excel = gr.Button("📊 Exportar a Excel", elem_classes="btn-secondary")
            btn_export_pdf = gr.Button("📄 Exportar a PDF", elem_classes="btn-secondary")
            btn_logout_profesor = gr.Button("🚪 Cerrar Sesión", elem_classes="btn-secondary")
        
        with gr.Row():
            archivo_descarga = gr.File(label="Archivo generado", visible=False)
            msg_export = gr.Markdown("")
    
    # ========== VISTA TUTOR ==========
    with gr.Group(visible=False, elem_classes="panel-card fade-in") as tutor_view:
        welcome_tutor = gr.Markdown("", elem_classes="welcome-box")
        
        info_tutor = gr.Markdown("")
        
        gr.Markdown("---")
        btn_logout_tutor = gr.Button("🚪 Cerrar Sesión", elem_classes="btn-secondary")
    
    # ========== LÓGICA DE NAVEGACIÓN ==========
    
    def router(username, password):
        """Enruta al usuario según su rol"""
        rol, mensaje, nombre_real = procesar_login(username, password)
        
        # Estados base (todo oculto)
        updates = {
            login_view: gr.update(visible=False),
            alumno_view: gr.update(visible=False),
            profesor_view: gr.update(visible=False),
            tutor_view: gr.update(visible=False),
            login_msg: "",
            welcome_alumno: "",
            welcome_profesor: "",
            welcome_tutor: "",
            tabla_informes: None,
            stat_total: "",
            stat_pendientes: "",
            stat_proceso: "",
            stat_resueltos: "",
            info_tutor: "",
            estado_usuario: nombre_real,
        }
        
        if rol == "error":
            updates[login_view] = gr.update(visible=True)
            updates[login_msg] = f"<div class='message-error'>{mensaje}</div>"
            return list(updates.values())
        
        if rol == "alumno":
            updates[alumno_view] = gr.update(visible=True)
            updates[welcome_alumno] = f"### {mensaje}\n\n📌 Estás en modo de reporte confidencial."
        
        elif rol in ["director", "profesor"]:
            total, pend, proc, resueltos, graves = obtener_estadisticas()
            df = obtener_datos_dashboard()
            
            updates[profesor_view] = gr.update(visible=True)
            updates[welcome_profesor] = f"### {mensaje}"
            updates[tabla_informes] = df
            updates[stat_total] = f"<div class='stat-card'><div class='stat-number'>{total}</div><div class='stat-label'>Total Informes</div></div>"
            updates[stat_pendientes] = f"<div class='stat-card'><div class='stat-number' style='color: #F59E0B;'>{pend}</div><div class='stat-label'>Pendientes</div></div>"
            updates[stat_proceso] = f"<div class='stat-card'><div class='stat-number' style='color: #818CF8;'>{proc}</div><div class='stat-label'>En Proceso</div></div>"
            updates[stat_resueltos] = f"<div class='stat-card'><div class='stat-number' style='color: #10B981;'>{resueltos}</div><div class='stat-label'>Resueltos</div></div>"
        
        elif rol == "tutor":
            updates[tutor_view] = gr.update(visible=True)
            updates[welcome_tutor] = f"### {mensaje}"
            updates[info_tutor] = obtener_info_tutor(nombre_real)
        
        return list(updates.values())
    
    def logout():
        """Cierra sesión y vuelve al login"""
        return (
            gr.update(visible=True),   # login_view
            gr.update(visible=False),  # alumno_view
            gr.update(visible=False),  # profesor_view
            gr.update(visible=False),  # tutor_view
            "",  # login_msg
            "",  # estado_usuario
        )
    
    def aplicar_filtros(desde, hasta, tipo, estado):
        """Aplica filtros a la tabla"""
        df = obtener_datos_dashboard(desde, hasta, tipo, estado)
        return df
    
    def actualizar_dashboard():
        """Actualiza el dashboard completo"""
        total, pend, proc, resueltos, graves = obtener_estadisticas()
        df = obtener_datos_dashboard()
        
        return (
            df,
            f"<div class='stat-card'><div class='stat-number'>{total}</div><div class='stat-label'>Total Informes</div></div>",
            f"<div class='stat-card'><div class='stat-number' style='color: #F59E0B;'>{pend}</div><div class='stat-label'>Pendientes</div></div>",
            f"<div class='stat-card'><div class='stat-number' style='color: #818CF8;'>{proc}</div><div class='stat-label'>En Proceso</div></div>",
            f"<div class='stat-card'><div class='stat-number' style='color: #10B981;'>{resueltos}</div><div class='stat-label'>Resueltos</div></div>",
        )
    
    def handle_export_excel(desde, hasta, tipo, estado):
        """Maneja exportación a Excel"""
        filepath, msg = exportar_excel(desde, hasta, tipo, estado)
        if filepath:
            return gr.update(visible=True, value=filepath), msg
        return gr.update(visible=False), msg
    
    def handle_export_pdf(desde, hasta, tipo, estado):
        """Maneja exportación a PDF"""
        filepath, msg = exportar_pdf(desde, hasta, tipo, estado)
        if filepath:
            return gr.update(visible=True, value=filepath), msg
        return gr.update(visible=False), msg
    
    # ========== FUNCIONES DE CHAT ==========
    
    def responder_chat(mensaje, historial):
        """Procesa el mensaje del usuario y devuelve la respuesta del chatbot"""
        if not mensaje:
            return historial, ""
        
        # Añadir mensaje del usuario al historial
        historial = historial or []
        
        # Obtener respuesta del agente
        respuesta = responder_alumno(historial, mensaje)
        
        # Añadir al historial
        historial.append((mensaje, respuesta))
        
        return historial, ""
    
    # ========== CONEXIONES DE EVENTOS ==========
    
    # Chat del alumno
    btn_enviar_msg.click(
        responder_chat,
        inputs=[txt_mensaje, chatbot_alumno],
        outputs=[chatbot_alumno, txt_mensaje]
    )
    
    txt_mensaje.submit(
        responder_chat,
        inputs=[txt_mensaje, chatbot_alumno],
        outputs=[chatbot_alumno, txt_mensaje]
    )
    
    # Login
    login_btn.click(
        router,
        inputs=[user_input, pass_input],
        outputs=[
            login_view, alumno_view, profesor_view, tutor_view,
            login_msg, welcome_alumno, welcome_profesor, welcome_tutor,
            tabla_informes, stat_total, stat_pendientes, stat_proceso, stat_resueltos,
            info_tutor, estado_usuario
        ]
    )
    
    # Enter para login
    pass_input.submit(
        router,
        inputs=[user_input, pass_input],
        outputs=[
            login_view, alumno_view, profesor_view, tutor_view,
            login_msg, welcome_alumno, welcome_profesor, welcome_tutor,
            tabla_informes, stat_total, stat_pendientes, stat_proceso, stat_resueltos,
            info_tutor, estado_usuario
        ]
    )
    
    # Enviar informe alumno
    btn_enviar_informe.click(
        guardar_informe_bd,
        inputs=[chatbot_alumno, estado_usuario],
        outputs=[resultado_envio]
    )
    
    # Logout buttons
    btn_logout_alumno.click(
        logout,
        outputs=[login_view, alumno_view, profesor_view, tutor_view, login_msg, estado_usuario]
    )
    btn_logout_profesor.click(
        logout,
        outputs=[login_view, alumno_view, profesor_view, tutor_view, login_msg, estado_usuario]
    )
    btn_logout_tutor.click(
        logout,
        outputs=[login_view, alumno_view, profesor_view, tutor_view, login_msg, estado_usuario]
    )
    
    # Filtros profesor
    btn_filtrar.click(
        aplicar_filtros,
        inputs=[filtro_fecha_desde, filtro_fecha_hasta, filtro_tipo, filtro_estado],
        outputs=[tabla_informes]
    )
    
    btn_refresh.click(
        actualizar_dashboard,
        outputs=[tabla_informes, stat_total, stat_pendientes, stat_proceso, stat_resueltos]
    )
    
    # Cambiar estado
    btn_cambiar_estado.click(
        cambiar_estado_informe,
        inputs=[input_id_informe, select_nuevo_estado],
        outputs=[resultado_cambio]
    ).then(
        actualizar_dashboard,
        outputs=[tabla_informes, stat_total, stat_pendientes, stat_proceso, stat_resueltos]
    )
    
    # Exportar
    btn_export_excel.click(
        handle_export_excel,
        inputs=[filtro_fecha_desde, filtro_fecha_hasta, filtro_tipo, filtro_estado],
        outputs=[archivo_descarga, msg_export]
    )
    
    btn_export_pdf.click(
        handle_export_pdf,
        inputs=[filtro_fecha_desde, filtro_fecha_hasta, filtro_tipo, filtro_estado],
        outputs=[archivo_descarga, msg_export]
    )


# --- 5. EJECUCIÓN ---
if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        ssl_certfile=os.getenv("SSL_CERTFILE"),  # ciber os pasa la ruta
        ssl_keyfile=os.getenv("SSL_KEYFILE"),    # ciber os pasa la ruta
    )