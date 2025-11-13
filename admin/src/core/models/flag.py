from datetime import datetime
from src.web.extensions import db
from typing import Any, Optional

# ELIMINADA: from flask_login import current_user  <- ¡Correcto!

class Flag(db.Model):
    __tablename__ = "Flag"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    message = db.Column(db.String(255), nullable=True)
    last_modified_at = db.Column(db.DateTime, nullable=True)
    last_modified_by = db.Column(db.String(120), nullable=True)

    def set_enabled(self, enabled: bool, actor: Optional[Any] = None, msg: Optional[str] = None) -> None:
        """
        Cambia estado del flag y actualiza auditoría.
        'actor' debe ser el objeto User pasado desde el servicio.
        """
        self.enabled = bool(enabled)

        if msg is not None:
            self.message = msg

        self.last_modified_at = datetime.utcnow()

        if actor:
            if hasattr(actor, "mail"):
                self.last_modified_by = actor.mail
            elif hasattr(actor, "username"):
                self.last_modified_by = actor.username
            elif hasattr(actor, "name"):
                self.last_modified_by = actor.name
            else:
                self.last_modified_by = str(actor)
        else:
            self.last_modified_by = "Sistema/Desconocido"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "message": self.message,
            "last_modified_at": self.last_modified_at.isoformat() if self.last_modified_at else None,
            "last_modified_by": self.last_modified_by
        }