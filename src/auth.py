# src/auth.py
from __future__ import annotations

import re
from flask import Blueprint, jsonify, request, current_app
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_limiter import Limiter
from sqlalchemy.exc import IntegrityError

from .database import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

bcrypt = Bcrypt()

# El Limiter lo inicializamos en main.py y lo inyectamos con init_app.
limiter: Limiter | None = None


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _bad_request(msg: str = "Invalid request"):
    return jsonify({"error": msg}), 400


@auth_bp.post("/register")
@jwt_required(optional=True)
def register():
    """
    En producción, normalmente NO expondría registro público para un instituto.
    Aun así lo dejo para pruebas/MVP.
    """
    data = request.get_json(silent=True) or {}
    email = _normalize_email(str(data.get("email", "")))
    password = str(data.get("password", ""))
    role = str(data.get("role", "")).upper()

    if not email or not EMAIL_RE.match(email):
        return _bad_request("Invalid request")
    if not password or len(password) < 10:
        # evita políticas raras; solo mínimo razonable
        return _bad_request("Invalid request")
    if role not in {"STUDENT", "GUARDIAN", "TEACHER"}:
        return _bad_request("Invalid request")

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=pw_hash, role=role, is_active=True)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Respuesta genérica para evitar enumeración
        return jsonify({"error": "Invalid request"}), 400

    return jsonify({"id": user.id, "email": user.email, "role": user.role}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = _normalize_email(str(data.get("email", "")))
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({"error": "Invalid credentials"}), 401

    user = User.query.filter_by(email=email).first()

    # Respuesta uniforme para evitar user enumeration (A07)
    if (not user) or (not user.is_active) or (not bcrypt.check_password_hash(user.password_hash, password)):
        current_app.logger.info("LOGIN_FAIL email=%s ip=%s", email, request.remote_addr)
        return jsonify({"error": "Invalid credentials"}), 401

    # JWT corto recomendado (A01 menciona tokens de corta duración) :contentReference[oaicite:7]{index=7}
    access = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh = create_refresh_token(identity=str(user.id), additional_claims={"role": user.role})

    current_app.logger.info("LOGIN_OK user_id=%s ip=%s", user.id, request.remote_addr)
    return jsonify({"access_token": access, "refresh_token": refresh}), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    claims = get_jwt()  # contiene role, etc.
    role = claims.get("role", "UNKNOWN")
    access = create_access_token(identity=user_id, additional_claims={"role": role})
    return jsonify({"access_token": access}), 200


# (Opcional MVP) Logout con blacklist en memoria: útil, pero en prod usar Redis
REVOKED_JTIS: set[str] = set()


@auth_bp.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt().get("jti")
    if jti:
        REVOKED_JTIS.add(jti)
    return jsonify({"ok": True}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"id": user.id, "email": user.email, "role": user.role}), 200
