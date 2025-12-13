# src/student.py
from __future__ import annotations

from flask import Blueprint, jsonify
from .authz import require_roles

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


@student_bp.get("/ping")
@require_roles("STUDENT", "GUARDIAN")
def ping_student():
    return jsonify({"ok": True, "scope": "student_portal"}), 200


# Aquí irán después:
# - POST /cases
# - POST /cases/<id>/finalize
# - GET /cases
