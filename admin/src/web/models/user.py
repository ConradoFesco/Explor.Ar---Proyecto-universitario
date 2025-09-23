from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'User'
    
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean)
    role = db.Column(db.String(20), default='user')
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
            'rol': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'blocked': self.blocked,
            'deleted': self.deleted
        }
    
    # --- Métodos de password ---
    def set_password(self, password):
        """Genera y guarda un hash seguro del password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si el password ingresado coincide con el hash guardado"""
        return check_password_hash(self.password_hash, password)

    # --- Permisos del usuario ---
    @property
    def permissions(self):
        perms = []
        for rol_rel in self.user_roles:   # recorre la relación User ↔ RolUser
            rol = rol_rel.rol_user
            for perm in rol.permissions:
                if perm.code not in perms:
                    perms.append(perm.code)
        return perms
