from src.web.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import Index


class User(db.Model):
    """
    Clase base para usuarios del sistema.
    Implementa Joined Table Inheritance para separar usuarios privados y públicos.
    """
    __tablename__ = 'User'
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': 'type'
    }

    # Campos compartidos
    id = db.Column(db.Integer, primary_key=True)
    # mail NO es único globalmente, solo dentro de cada subtipo (PrivateUser o PublicUser)
    mail = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos de soft delete (aplican a ambos tipos por trazabilidad y requerimientos legales)
    deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by_id = db.Column(db.Integer, nullable=True)
    
    # Campo discriminador para polimorfismo
    type = db.Column(db.String(50), nullable=False)
    
    # Índice único compuesto: el mail es único dentro de cada tipo (private/public)
    # Permite que exista un PrivateUser y un PublicUser con el mismo mail
    # pero no permite duplicados dentro del mismo tipo
    __table_args__ = (
        Index('idx_user_type_mail_unique', 'type', 'mail', unique=True),
    )

    def __repr__(self) -> str:
        return f'<User {self.name} {self.last_name}>'

    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna un diccionario con los campos compartidos de la clase base.
        Las subclases deben extender este método para incluir sus campos específicos.
        """
        return {
            'id': self.id,
            'mail': self.mail,
            'name': self.name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deleted': self.deleted,
        }


class PrivateUser(User):
    """
    Usuario interno del sistema con autenticación, roles y permisos.
    Maneja eventos y gestión administrativa.
    """
    __tablename__ = 'Private_User'
    __mapper_args__ = {
        'polymorphic_identity': 'private'
    }

    # Foreign key a la tabla base
    id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    
    # Campos privados de autenticación y gestión
    password = db.Column(db.String, nullable=True)
    active = db.Column(db.Boolean)
    blocked = db.Column(db.Boolean)
    is_super_admin = db.Column(db.Boolean, default=False)

    # Relaciones específicas de usuarios privados
    events = db.relationship('Event', backref='user', lazy=True)
    user_roles = db.relationship('RolUserUser', backref='user', lazy=True)

    def __repr__(self) -> str:
        return f'<PrivateUser {self.name} {self.last_name}>'

    def to_dict(self) -> Dict[str, Any]:
        """Extiende el to_dict de la clase base con campos privados."""
        base_dict = super().to_dict()
        base_dict.update({
            'active': self.active,
            'blocked': self.blocked,
            'is_super_admin': self.is_super_admin,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'deleted_by_id': self.deleted_by_id,
        })
        return base_dict

    def set_password(self, password_plain: str) -> None:
        """Genera y guarda un hash seguro del password"""
        self.password = generate_password_hash(password_plain)

    def check_password(self, password_plain: str) -> bool:
        """Verifica si el password ingresado coincide con el hash guardado"""
        if not self.password:
            return False
        return check_password_hash(self.password, password_plain)

    def has_permission(self, permission_name: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico de forma eficiente.
        
        Args:
            permission_name (str): Nombre del permiso a verificar
            
        Returns:
            bool: True si tiene el permiso, False en caso contrario
        """
        if self.is_super_admin:
            return True
        
        for rol_rel in self.user_roles:
            rol = rol_rel.rol_user
            for perm_rel in rol.permission_rol_users:
                if perm_rel.permission.name == permission_name:
                    return True
        
        return False

    def get_user_roles(self) -> List[str]:
        """Retorna los nombres de los roles del usuario."""
        return [rol_rel.rol_user.name for rol_rel in self.user_roles]


class PublicUser(User):
    """
    Usuario público del sistema (OAuth externo, ej: Google).
    Solo lectura básica, puede tener reseñas y favoritos.
    """
    __tablename__ = 'Public_User'
    __mapper_args__ = {
        'polymorphic_identity': 'public'
    }

    # Foreign key a la tabla base
    id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    
    # Campo específico de usuarios públicos
    avatar_url = db.Column(db.String, nullable=True)

    # Relaciones específicas de usuarios públicos
    favorites = db.relationship('FavoriteSite', backref='user', lazy=True)
    # reviews - la relación inversa ya está definida en HistoricSiteReview con user
    reviews = db.relationship('HistoricSiteReview', foreign_keys='HistoricSiteReview.user_id', lazy=True)

    def __repr__(self) -> str:
        return f'<PublicUser {self.name} {self.last_name}>'

    def to_dict(self) -> Dict[str, Any]:
        """Extiende el to_dict de la clase base con campos públicos."""
        base_dict = super().to_dict()
        base_dict.update({
            'avatar_url': self.avatar_url,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'deleted_by_id': self.deleted_by_id,
        })
        return base_dict
    