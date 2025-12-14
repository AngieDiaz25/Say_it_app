import gradio as gr
import os
import pandas as pd
from flask import Flask
from backend.models import db, Alumno, CentroEstudios, Informe, Director, Tutor
from backend.auth import autenticar_usuario
from backend.agents import responder_alumno, generar_reporte_riesgo
from backend.reporting import generar_pdf_informe

# --- CONFIGURACIÓN ---
app = Flask(__name__)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
db_path = os.path.join(base_dir, 'bullying.db')

# Asegurar que la carpeta data existe
os.makedirs(base_dir, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- BACKEND ---

def procesar_login(email, password):
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
    if not historial_chat: return "⚠️ Formulario vacío. Di 'Hola' para empezar."

    print("--- INICIANDO GUARDADO ---")
    
    # 1. Análisis IA
    try:
        datos = generar_reporte_riesgo(historial_chat)
    except Exception as e:
        print(f"Error IA: {e}")
        datos = {"rol_informante": "Error", "resumen_hechos": "Fallo análisis", "nivel_gravedad": "REVISAR"}

    # 2. Datos para BD (LIMPIEZA Y VALIDACIÓN)
    rol_informante = datos.get("rol_informante", "TESTIGO")
    resumen = datos.get("resumen_hechos", "Sin detalles")
    
    # Corrección de lista a string
    tipo_raw = datos.get("tipo_incidente", "Otro")
    if isinstance(tipo_raw, list):
        tipo = ", ".join(tipo_raw)
    else:
        tipo = str(tipo_raw)

    with app.app_context():
        # BUSCAR POR EMAIL (CAMBIO IMPORTANTE)
        informante = Alumno.query.filter_by(email_alumno=usuario_email).first()
        
        if informante:
            centro = CentroEstudios.query.get(informante.id_centro_estudios)
            
            nombre_centro = "Centro Desconocido"
            id_director_destino = None
            
            if centro:
                try:
                    gen = centro.denominacion_generica_es or ""
                    esp = centro.denominacion_especifica or ""
                    nombre_centro = f"{gen} {esp}".strip()
                    
                    if centro.id_director:
                        director = Director.query.get(centro.id_director)
                        if director:
                            id_director_destino = director.id_director
                except Exception as e:
                    print(f"Error obteniendo datos centro: {e}")

            # 3. Guardar en BD
            try:
                nuevo_informe = Informe(
                    tipo_bullying=tipo,
                    descripcion=f"[{rol_informante}] {resumen}",
                    id_centro_estudios=informante.id_centro_estudios,
                    id_director=id_director_destino
                )
                db.session.add(nuevo_informe)
                db.session.commit()
                
                ruta_pdf = generar_pdf_informe(nuevo_informe.id_informe, datos, historial_chat, nombre_centro)
                
                return f"✅ EXPEDIENTE #{nuevo_informe.id_informe} CREADO.\n📄 PDF generado en: {ruta_pdf}\nEl caso ha sido derivado a Dirección."
            
            except Exception as e:
                print(f"Error SQL: {e}")
                return f"❌ Error guardando en base de datos: {e}"
        
        else:
            return "❌ Error: No se encuentra el alumno (Email no reconocido)."

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
            print(f"Error dashboard: {e}")
            return pd.DataFrame(columns=["Error"])

# --- INTERFAZ ---
theme = gr.themes.Soft()

with gr.Blocks(theme=theme, title="Say It - Gestión Escolar") as demo:
    
    estado_rol = gr.State("")
    estado_usuario = gr.State("") # Ahora guardará el EMAIL

    gr.Markdown("# 🛡️ Say It: Sistema de Denuncia y Gestión")
    
    # LOGIN
    with gr.Group(visible=True) as login_view:
        with gr.Row():
            # CAMBIO VISUAL: Label ahora pide Email
            user_input = gr.Textbox(label="Email Corporativo", placeholder="ejemplo: micaela.hervia@sayit.edu")
            pass_input = gr.Textbox(label="Contraseña", type="password", placeholder="1234")
        login_btn = gr.Button("Acceder", variant="primary")
        login_msg = gr.Markdown("")

    # ALUMNO
    with gr.Group(visible=False) as chat_view:
        gr.Markdown("### 📝 Nueva Denuncia")
        gr.Markdown("Responde a las preguntas para abrir un expediente oficial.")
        chatbot = gr.ChatInterface(
            fn=lambda m, h: responder_alumno(h, m),
            chatbot=gr.Chatbot(height=350),
            textbox=gr.Textbox(placeholder="Escribe aquí...", scale=5),
        )
        btn_enviar = gr.Button("🚨 FINALIZAR Y GENERAR EXPEDIENTE PDF", variant="stop")
        confirmacion = gr.Textbox(label="Resultado del Proceso", interactive=False)

    # DIRECTOR
    with gr.Group(visible=False) as admin_view:
        gr.Markdown("### 📂 Dirección - Expedientes Recibidos")
        btn_refresh = gr.Button("🔄 Actualizar Bandeja")
        tabla = gr.Dataframe(label="Denuncias", interactive=False, wrap=True)
        gr.Markdown("ℹ️ *Los PDFs se guardan automáticamente en la carpeta data/reports.*")

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