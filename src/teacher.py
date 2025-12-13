# src/teacher.py
from __future__ import annotations

from flask import Blueprint, jsonify
from .authz import require_roles

teacher_bp = Blueprint("teacher", __name__, url_prefix="/api/teacher")


@teacher_bp.get("/ping")
@require_roles("TEACHER")
def ping_teacher():
    return jsonify({"ok": True, "scope": "teacher_portal"}), 200


# Aquí irán después las 5 pestañas:
# - GET /forms?status=pending|read
# - POST /forms/<id>/mark-read
# - GET /protocol
# - GET /tools
# - GET /history
