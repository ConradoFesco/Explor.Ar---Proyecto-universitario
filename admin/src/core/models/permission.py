from src.web.extensions import db
from typing import Dict, Any


class Permission(db.Model):
    __tablename__ = 'Permission'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    deleted = db.Column(db.Boolean, default=False)
    
    permission_rol_users = db.relationship('PermissionRolUser', backref='permission', lazy=True)
    
    def __repr__(self) -> str:
        return f'<Permission {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'deleted': self.deleted
        }
