from src.web.extensions import db

class RolUser(db.Model):
    __tablename__ = 'Rol_User'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    deleted = db.Column(db.Boolean, default=False)
    
    # Relaciones
    permission_rol_users = db.relationship('PermissionRolUser', backref='rol_user', lazy=True)
    rol_user_users = db.relationship('RolUserUser', backref='rol_user', lazy=True)
    
    def __repr__(self):
        return f'<RolUser {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'deleted': self.deleted
        }
