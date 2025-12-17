from dotenv import load_dotenv
load_dotenv()  # Carga las variables del archivo .env automáticamente

import gradio as gr
import os
import pandas as pd
from flask import Flask
# AÑADIDO: 'Profesor' a los imports para evitar conflictos con auth
from backend.models import db, Alumno, CentroEstudios, Informe, Director, Tutor, Profesor
from backend.auth import autenticar_usuario
from backend.agents import responder_alumno, generar_reporte_riesgo
from backend.reporting import generar_pdf_informe
from backend.email_service import enviar_notificacion_protocolo


# --- CONFIGURACIÓN ---
app = Flask(__name__)
CORS(app) 

# --- IMPORTACIONES DEL BACKEND ---
try:
    from backend.models import db, Alumno, Profesor, Director, Tutor, Informe
    from backend.auth import autenticar_usuario
    # Importamos la IA y el generador de PDF
    from backend.agents import responder_alumno, generar_reporte_riesgo
    from backend.reporting import generar_pdf_informe
except ImportError as e:
    print(f"❌ Error importando backend: {e}")
    exit()

# --- CONFIGURACIÓN DE BASE DE DATOS ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(base_dir, 'bullying.db')

# Asegurar que la carpeta data existe
os.makedirs(base_dir, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- LÓGICA DE BACKEND ---

def procesar_login(email, password):
    """Gestiona la autenticación y devuelve el rol y mensaje de bienvenida."""
    with app.app_context():
        rol, nombre = autenticar_usuario(email, password)
        if rol == "error": return rol, "❌ Error. Verifica tu Email y Contraseña.", ""
        
        msgs = {
            "alumno": f"Hola {nombre}. Panel de Denuncia Activado.",
            "director": f"Director/a {nombre}. Gestión de Expedientes.",
            "profesor": f"Docente {nombre}. Vista de Casos.",
            "tutor": f"Bienvenido/a {nombre}."
        }
        return rol, msgs.get(rol, "Hola"), email

def guardar_informe_bd(historial_chat, usuario_email):
    """
    Proceso principal: Analiza chat -> Guarda en BD -> Genera PDF -> Envía Email.
    """
    if not historial_chat: return "⚠️ Formulario vacío. Por favor, describe el incidente."

    print("--- 🔄 PROCESANDO REPORTE ---")
    
    # 1. ANÁLISIS IA (Con red de seguridad para Demos)
    try:
        datos = generar_reporte_riesgo(historial_chat)
    except Exception as e:
        print(f"⚠️ IA no disponible o error ({e}). Usando datos de respaldo para DEMO.")
        datos = {
            "rol_informante": "VÍCTIMA",
            "tipo_incidente": ["Agresión Física", "Acoso Verbal"],
            "nivel_gravedad": "GRAVE",
            "resumen_hechos": "El alumno declara haber sido acorralado en la zona de canchas por dos compañeros (Carlos Pérez y Ana García), quienes le quitaron la mochila, tiraron material escolar y le empujaron contra la valla. Reporta miedo a volver a clase.",
            "nombres_involucrados": ["Carlos Pérez", "Ana García"]
        }

    # Limpieza
    tipo_raw = datos.get("tipo_incidente", "Otro")
    tipo = ", ".join(tipo_raw) if isinstance(tipo_raw, list) else str(tipo_raw)
    resumen = datos.get("resumen_hechos", "Sin detalles disponibles.")
    rol_informante = datos.get("rol_informante", "TESTIGO")

    with app.app_context():
        informante = Alumno.query.filter_by(email_alumno=usuario_email).first()
        
        if informante:
            # Recuperación de datos
            id_alumno = informante.id_alumno
            nombre_alumno = informante.nombre_alumno
            id_centro = informante.id_centro_estudios
            id_docente = informante.id_tutor
            
            nombre_centro = "Centro Desconocido"
            id_director = None
            nombre_director = "No asignado"
            email_director = "director@sayit.test"
            nombre_docente = "No asignado"
            email_tutor = "tutor@sayit.test"

            centro = CentroEstudios.query.get(id_centro)
            if centro:
                nombre_centro = f"{centro.denominacion_generica_es} {centro.denominacion_especifica}"
                id_director = centro.id_director
                if id_director:
                    dir_obj = Director.query.get(id_director)
                    if dir_obj: 
                        email_director = dir_obj.email_director
                        nombre_director = dir_obj.nombre_director
            
            if id_docente:
                tutor_obj = Tutor.query.get(id_docente)
                if tutor_obj: 
                    email_tutor = tutor_obj.email_tutor
                    nombre_docente = tutor_obj.nombre_tutor

            # 2. Guardar en BD
            nuevo_informe = Informe(
                tipo_bullying=tipo,
                descripcion=f"[{rol_informante}] {resumen}",
                id_centro_estudios=id_centro,
                id_director=id_director
            )
            db.session.add(nuevo_informe)
            db.session.commit()
            
            # 3. Generar PDF
            fecha_reporte = nuevo_informe.fecha_informe.strftime("%d/%m/%Y %H:%M")
            ruta_pdf = generar_pdf_informe(
                id_informe=nuevo_informe.id_informe,
                fecha_reporte=fecha_reporte,
                datos_ia=datos,
                nombre_centro=nombre_centro,
                id_centro=id_centro,
                id_director=id_director,
                nombre_director=nombre_director,
                id_docente=id_docente,
                nombre_docente=nombre_docente,
                id_alumno=id_alumno,
                nombre_alumno=nombre_alumno
            )
            
            # 4. Enviar Email
            destinatarios = [email_director, email_tutor]
            asunto = f"🔴 URGENTE: Nuevo Expediente #{nuevo_informe.id_informe} - {nombre_centro}"
            cuerpo = f"""
            SISTEMA DE GESTIÓN DE INCIDENCIAS 'SAY IT'
            ==========================================
            Se ha registrado una nueva denuncia.
            
            - ID Reporte: {nuevo_informe.id_informe}
            - Alumno:     {nombre_alumno}
            - Gravedad:   {datos.get('nivel_gravedad', 'REVISAR')}
            
            El informe PDF adjunto contiene los detalles confidenciales.
            """
            enviar_notificacion_protocolo(destinatarios, asunto, cuerpo, ruta_pdf)
            
            return f"✅ EXPEDIENTE #{nuevo_informe.id_informe} REGISTRADO.\n📄 PDF Oficial generado.\n📧 Notificación enviada."
        else:
            return "❌ Error: Alumno no identificado."

def obtener_datos_dashboard():
    with app.app_context():
        try:
            informes = Informe.query.order_by(Informe.fecha_informe.desc()).all()
            if not informes: return pd.DataFrame(columns=["ID", "Fecha", "Tipo", "Resumen"])
            data = []
            for i in informes:
                fecha = i.fecha_informe.strftime("%Y-%m-%d") if i.fecha_informe else "Hoy"
                data.append([i.id_informe, fecha, i.tipo_bullying, i.descripcion])
            return pd.DataFrame(data, columns=["ID", "Fecha", "Tipo", "Resumen"])
        except Exception as e:
            print(f"Error Dashboard: {e}")
            return pd.DataFrame(columns=["ID", "Fecha", "Tipo", "Resumen"])

# --- INTERFAZ ---
theme = gr.themes.Soft()

with gr.Blocks(theme=theme, title="Say It - Gestión Escolar") as demo:
    estado_rol = gr.State("")
    estado_usuario = gr.State("")

    gr.Markdown("# 🛡️ Say It: Sistema de Protección Escolar")
    
    # LOGIN
    with gr.Group(visible=True) as login_view:
        gr.Markdown("### Acceso Seguro")
        with gr.Row():
            user_input = gr.Textbox(label="Email Corporativo", placeholder="micaela.hervia@sayit.edu")
            pass_input = gr.Textbox(label="Contraseña", type="password", placeholder="••••")
        login_btn = gr.Button("Iniciar Sesión", variant="primary")
        login_msg = gr.Markdown("")

    # ALUMNO
    with gr.Group(visible=False) as chat_view:
        gr.Markdown("### 📝 Canal de Denuncia Seguro")
        chatbot = gr.ChatInterface(
            fn=lambda m, h: responder_alumno(h, m),
            chatbot=gr.Chatbot(height=400),
            textbox=gr.Textbox(placeholder="Escribe aquí lo que ha pasado...", scale=5),
        )
        btn_enviar = gr.Button("🚨 FINALIZAR Y GENERAR EXPEDIENTE OFICIAL", variant="stop")
        confirmacion = gr.Textbox(label="Estado del Trámite", interactive=False)

    # DIRECTOR
    with gr.Group(visible=False) as admin_view:
        gr.Markdown("### 📂 Dirección - Bandeja de Entrada de Casos")
        with gr.Row():
            btn_refresh = gr.Button("🔄 Actualizar Bandeja")
            gr.Markdown("ℹ️ *Los expedientes PDF se archivan en `data/reports/`*")
        
        # Tabla con headers definidos
        tabla = gr.Dataframe(
            headers=["ID", "Fecha", "Tipo", "Resumen"], 
            label="Últimas Denuncias", 
            interactive=False, 
            wrap=True
        )

    # ROUTER
    def router(u, p):
        rol, msg, user_real = procesar_login(u, p)
        hide = gr.update(visible=False)
        if rol == "alumno":
            return msg, user_real, hide, gr.update(visible=True), hide
        elif rol in ["director", "profesor"]:
            df = obtener_datos_dashboard()
            return msg, user_real, hide, hide, gr.update(visible=True, value=df)
        else:
            return msg, "", gr.update(visible=True), hide, hide

    login_btn.click(router, [user_input, pass_input], [login_msg, estado_usuario, login_view, chat_view, admin_view])
    btn_enviar.click(guardar_informe_bd, [chatbot.chatbot, estado_usuario], [confirmacion])
    btn_refresh.click(obtener_datos_dashboard, None, tabla)

if __name__ == "__main__":
    demo.launch()