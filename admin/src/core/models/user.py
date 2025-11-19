from src.web.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import List, Dict, Any

class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=True)
    active = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    blocked = db.Column(db.Boolean)
    is_super_admin = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deletion_reason = db.Column(db.String(255), nullable=True)
    deleted_by_id = db.Column(db.Integer, nullable=True)
    avatar_url = db.Column(db.String, nullable=True)

    # Relaciones
    events = db.relationship('Event', backref='user', lazy=True)
    user_roles = db.relationship('RolUserUser', backref='user', lazy=True)
    favorites = db.relationship('FavoriteSite', backref='user', lazy=True)

    def __repr__(self) -> str:
        return f'<User {self.name} {self.last_name}>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'mail': self.mail,
            'name': self.name,
            'last_name': self.last_name,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'blocked': self.blocked,
            'deleted': self.deleted,
            'is_super_admin': self.is_super_admin
        }

    # --- Métodos de password ---
    def set_password(self, password_plain: str) -> None:
        """Genera y guarda un hash seguro del password"""
        self.password = generate_password_hash(password_plain)

    def check_password(self, password_plain: str) -> bool:
        """Verifica si el password ingresado coincide con el hash guardado"""
        return check_password_hash(self.password, password_plain)

    # --- Permisos del usuario ---
    def has_permission(self, permission_name: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico de forma eficiente.
        
        Args:
            permission_name (str): Nombre del permiso a verificar
            
        Returns:
            bool: True si tiene el permiso, False en caso contrario
        """
        # 1. Chequeo de Super-Admin (llave maestra)
        if self.is_super_admin:
            return True
        
        # 2. Chequeo normal - detiene búsqueda al encontrar el permiso
        for rol_rel in self.user_roles:
            rol = rol_rel.rol_user
            for perm_rel in rol.permission_rol_users:
                if perm_rel.permission.name == permission_name:
                    return True  # Retorna inmediatamente al encontrarlo
        
        return False  # No se encontró el permiso

    def get_user_roles(self) -> List[str]:
        """
        Retorna los nombres de los roles del usuario.

        """
        return [rol_rel.rol_user.name for rol_rel in self.user_roles]
    
    