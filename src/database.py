# src/database.py
from __future__ import annotations

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)

    # roles: "STUDENT", "GUARDIAN", "TEACHER"
    role: Mapped[str] = mapped_column(db.String(32), nullable=False)

    is_active: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
