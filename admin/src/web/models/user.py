
from datetime import datetime
from argon2 import PasswordHasher, exceptions
from .. import db
ph = PasswordHasher()

class User(db.Model):
    __tablename__ = 'User'
    
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    blocked = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean, default=False)
    
    # Relaciones
    events = db.relationship('Event', backref='user', lazy=True)
    user_roles = db.relationship('RolUserUser', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name} {self.last_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'mail': self.mail,
            'name': self.name,
            'last_name': self.last_name,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'blocked': self.blocked,
            'deleted': self.deleted
        }
    def set_password(self, raw_password: str):
        """Hashea la contraseña en crudo y la guarda."""
        self.password = ph.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash guardado."""
        try:
            return ph.verify(self.password, raw_password)
        except exceptions.VerifyMismatchError:
            return False
        except exceptions.InvalidHash:
            return False