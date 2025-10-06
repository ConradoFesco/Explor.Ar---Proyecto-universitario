from datetime import datetime
from src.web.extensions import db
from flask_login import current_user

class Flag(dbe.Model):
    __tablename__ = "feature_flags"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)   # nombre técnico del flag
    name = db.Column(db.String(120), nullable=False)               # nombre amigable
    description = db.Column(db.String(255), nullable=True)
    enabled = db.Column(db.Boolean, nullable=False, default=False) #estado
    message = db.Column(db.String(255), nullable=True)             # mensaje de mantenimiento
    last_modified_at = db.Column(db.DateTime, nullable=True)
    last_modified_by = db.Column(db.String(120), nullable=True)    # usuario que modificó

    def set_enabled(self, enabled: bool, actor=None, msg: str = None):
        """
        Cambia estado del flag y actualiza auditoría
        """
        self.enabled = bool(enabled)
        if msg is not None:
            self.message = msg
        self.last_modified_at = datetime.utcnow()
        if actor:
            if hasattr(actor, "email"):
                self.last_modified_by = actor.email
            elif hasattr(actor, "username"):
                self.last_modified_by = actor.username
            else:
                self.last_modified_by = str(actor)
        else:
            try:
                if current_user and hasattr(current_user, "email"):
                    self.last_modified_by = current_user.email
            except Exception:
                pass
