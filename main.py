# src/main.py
from __future__ import annotations

import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .database import db
from .auth import auth_bp, bcrypt, REVOKED_JTIS

jwt = JWTManager()


def create_app() -> Flask:
    app = Flask(__name__)

    # --- Config base ---
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///sayit.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT: corta duración (recomendación frecuente; minimiza ventana de ataque) :contentReference[oaicite:9]{index=9}
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    # Si más adelante metéis JWT en cookies:
    # app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    # app.config["JWT_COOKIE_SECURE"] = True
    # app.config["JWT_COOKIE_SAMESITE"] = "Lax"

    # --- Extensiones ---
    CORS(app, resources={r"/api/*": {"origins": os.environ.get("CORS_ORIGINS", "*")}})
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
    )

    # Rate limit más estricto para login (A07: limitar intentos / delay) :contentReference[oaicite:10]{index=10}
    limiter.limit("10 per minute")(auth_bp.view_functions.get("auth.login"))

    # --- JWT revocation (logout) ---
    @jwt.token_in_blocklist_loader
    def is_token_revoked(_jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        return jti in REVOKED_JTIS

    # --- Blueprints ---
    app.register_blueprint(auth_bp)

    # --- CLI init DB (MVP) ---
    @app.get("/health")
    def health():
        return {"ok": True}

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)



#REGISTRO DE BLUEPRINTS
# src/main.py
from .student import student_bp
from .teacher import teacher_bp

# ...
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)
