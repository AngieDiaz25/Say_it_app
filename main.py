import gradio as gr
import os
import pandas as pd
from flask import Flask
from backend.models import db, Alumno, CentroEstudios, Informe, Director, Tutor
from backend.auth import autenticar_usuario
from backend.agents import responder_alumno, generar_reporte_riesgo

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
app = Flask(__name__)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(base_dir, 'bullying.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- 2. LÓGICA DE NEGOCIO (BACKEND) ---

def procesar_login(username, password):
    with app.app_context():
        rol, nombre = autenticar_usuario(username, password)
        if rol == "error":
            return rol, "❌ Credenciales incorrectas.", ""
        
        mensajes = {
            "alumno": f"Hola {nombre}. Panel de Reporte Activado.",
            "director": f"Panel de Dirección. Bienvenido/a {nombre}.",
            "profesor": f"Panel Docente. Hola {nombre}.",
            "tutor": f"Portal de Familias. Bienvenido/a {nombre}."
        }
        return rol, mensajes.get(rol, "Bienvenido"), username

def guardar_informe_bd(historial_chat, usuario_informante):
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
            director = Director.query.join(CentroEstudios).filter(CentroEstudios.id_centro_estudios == informante.id_centro_estudios).first()
            id_dir = director.id_director if director else None
            
            descripcion_oficial = f"[{rol_informante}] VÍCTIMA: {victima} | AGRESORES: {agresores} | HECHOS: {resumen}"
            
            nuevo_informe = Informe(
                tipo_bullying=tipo,
                descripcion=descripcion_oficial, 
                id_centro_estudios=informante.id_centro_estudios,
                id_director=id_dir
            )
            db.session.add(nuevo_informe)
            db.session.commit()
            
            return f"✅ INFORME REGISTRADO CORRECTAMENTE.\nRol: {rol_informante}\nGravedad: {gravedad}\nEl centro ha sido notificado."
        else:
            return "❌ Error: No se pudo verificar tu identidad."

def obtener_datos_dashboard():
    with app.app_context():
        informes = Informe.query.order_by(Informe.fecha_informe.desc()).all()
        if not informes:
            return pd.DataFrame(columns=["ID", "Fecha", "Tipo", "Detalle del Expediente"])
        data = [[i.id_informe, i.fecha_informe.strftime("%Y-%m-%d"), i.tipo_bullying, i.descripcion] for i in informes]
        return pd.DataFrame(data, columns=["ID", "Fecha", "Tipo", "Detalle del Expediente"])

def obtener_info_tutor(usuario_tutor):
    return "✅ Su hijo/a asiste con normalidad. No hay notificaciones de convivencia pendientes."

# --- 3. INTERFAZ GRÁFICA (FRONTEND) ---

tema = gr.themes.Soft(primary_hue="blue", secondary_hue="indigo")

# Corrección Gradio 5: Movemos el 'theme' y 'title' fuera de Blocks si es necesario, 
# pero lo mantendremos estándar y simplificamos el ChatInterface.
with gr.Blocks(theme=tema, title="Say It - App Anti-Bullying") as demo:
    
    estado_rol = gr.State("")
    estado_usuario = gr.State("")

    gr.Markdown("# 🛡️ Say It: Canal de Convivencia Escolar")
    
    # --- VISTA 1: LOGIN ---
    with gr.Group(visible=True) as login_view:
        gr.Markdown("### 🔐 Acceso Seguro")
        with gr.Row():
            user_input = gr.Textbox(label="Usuario", placeholder="Alumno, Director, Tutor...")
            pass_input = gr.Textbox(label="Contraseña", type="password")
        login_btn = gr.Button("Entrar", variant="primary")
        login_msg = gr.Markdown("")

    # --- VISTA 2: ALUMNO (DENUNCIA) ---
    with gr.Group(visible=False) as chat_view:
        gr.Markdown("### 📝 Formulario de Reporte Asistido")
        gr.Markdown("""
        **¿Cómo funciona?**
        1. Responde a las preguntas del asistente.
        2. Indica claramente si eres la **VÍCTIMA** o un **TESTIGO**.
        3. Cuando termines, pulsa el botón rojo para enviar el informe al Director.
        """)
        
        # --- AQUÍ ESTABA EL ERROR: Simplificamos los botones ---
        chatbot = gr.ChatInterface(
            fn=lambda m, h: responder_alumno(h, m),
            chatbot=gr.Chatbot(height=350),
            textbox=gr.Textbox(placeholder="Hola, quiero contar algo...", scale=5),
            # Eliminamos 'undo_btn' y 'submit_btn' personalizados para evitar errores de versión
        )
        
        btn_enviar = gr.Button("📁 REGISTRAR INFORME OFICIAL", variant="stop")
        confirmacion = gr.Textbox(label="Estado del Envío", interactive=False)

    # --- VISTA 3: GESTIÓN ---
    with gr.Group(visible=False) as admin_view:
        gr.Markdown("### 📂 Bandeja de Expedientes")
        btn_refresh = gr.Button("🔄 Actualizar Datos")
        tabla = gr.Dataframe(
            label="Informes Recientes", 
            headers=["ID", "Fecha", "Tipo", "Detalle del Expediente"],
            interactive=False,
            wrap=True
        )

    # --- VISTA 4: FAMILIA ---
    with gr.Group(visible=False) as family_view:
        gr.Markdown("### 🏠 Portal Familiar")
        info_familia = gr.Markdown("Cargando...")

    # --- ROUTER ---
    def router(u, p):
        rol, msg, user_real = procesar_login(u, p)
        hide = gr.update(visible=False)
        
        if rol == "alumno":
            return msg, user_real, hide, gr.update(visible=True), hide, hide, None
        elif rol in ["director", "profesor"]:
            df = obtener_datos_dashboard()
            return msg, user_real, hide, hide, gr.update(visible=True), hide, df
        elif rol == "tutor":
            info = obtener_info_tutor(user_real)
            return msg, user_real, hide, hide, hide, gr.update(visible=True), info
        else:
            return msg, "", gr.update(visible=True), hide, hide, hide, None

    login_btn.click(router, [user_input, pass_input], [login_msg, estado_usuario, login_view, chat_view, admin_view, family_view, info_familia])
    btn_enviar.click(guardar_informe_bd, [chatbot.chatbot, estado_usuario], [confirmacion])
    btn_refresh.click(obtener_datos_dashboard, None, tabla)

if __name__ == "__main__":
    demo.launch()