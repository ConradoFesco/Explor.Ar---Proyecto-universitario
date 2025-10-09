from src.web.extensions import db

class PermissionRolUser(db.Model):
    __tablename__ = 'Permission_Rol_User'
    
    Permission_id = db.Column(db.Integer, db.ForeignKey('Permission.id'), primary_key=True)
    Rol_User_id = db.Column(db.Integer, db.ForeignKey('Rol_User.id'), primary_key=True)
    
    def __repr__(self):
        return f'<PermissionRolUser Permission:{self.Permission_id} Rol:{self.Rol_User_id}>'
    
    def to_dict(self):
        return {
            'Permission_id': self.Permission_id,
            'Rol_User_id': self.Rol_User_id
        }
