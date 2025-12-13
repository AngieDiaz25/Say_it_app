# src/authz.py
from __future__ import annotations

from functools import wraps
from typing import Callable, Iterable

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt


def require_roles(*allowed_roles: str) -> Callable:
    """
    Requiere JWT válido y que el claim 'role' esté en allowed_roles.
    Uso:
      @bp.get("/x")
      @require_roles("TEACHER")
      def handler(): ...
    """
    allowed = {r.upper() for r in allowed_roles}

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = str(claims.get("role", "")).upper()

            if role not in allowed:
                # No revelamos qué rol se esperaba
                return jsonify({"error": "Forbidden"}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator
