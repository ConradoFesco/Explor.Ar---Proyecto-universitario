from ..extensions import db

class Permission(db.Model):
    __tablename__ = 'Permission'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    deleted = db.Column(db.Boolean, default=False)
    
    # Relaciones
    permission_rol_users = db.relationship('PermissionRolUser', backref='permission', lazy=True)
    
    def __repr__(self):
        return f'<Permission {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'deleted': self.deleted
        }
