from src.web.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import List, Dict, Any, Set, Optional
from sqlalchemy import Index
from sqlalchemy.orm import joinedload


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

    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by_id = db.Column(db.Integer, nullable=True)
    
    type = db.Column(db.String(50), nullable=False)
    
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

    id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    
    password = db.Column(db.String, nullable=True)
    active = db.Column(db.Boolean)
    blocked = db.Column(db.Boolean)
    is_super_admin = db.Column(db.Boolean, default=False)

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

    def set_permissions(self, permissions: Set[str]) -> None:
        """
        Establece los permisos del usuario desde el servicio (hidratación).
        El modelo no debe buscar sus propios permisos, estos son inyectados por la capa de servicio.
        
        Args:
            permissions (Set[str]): Conjunto de nombres de permisos asignados al usuario.
        """
        self._cached_permissions = frozenset(permissions) if permissions else frozenset()
    
    def has_permission(self, permission_name: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico.
        Requiere que el usuario haya sido hidratado previamente con set_permissions().
        
        Args:
            permission_name (str): Nombre del permiso a verificar
            
        Returns:
            bool: True si tiene el permiso, False en caso contrario o si no está hidratado.
        """
        if self.is_super_admin:
            return True
        
        # Si no está hidratado, retornar False (no intentar cargar de BD)
        if not hasattr(self, '_cached_permissions') or self._cached_permissions is None:
            return False
        
        return permission_name in self._cached_permissions
    
    def invalidate_permissions_cache(self) -> None:
        """
        Invalida el cache de permisos, forzando una recarga en la próxima verificación.
        Debe llamarse cuando se modifican los roles o permisos del usuario.
        """
        if hasattr(self, '_cached_permissions'):
            self._cached_permissions = None

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

    id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    
    avatar_url = db.Column(db.String, nullable=True)

    favorites = db.relationship('FavoriteSite', backref='user', lazy=True)
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
    