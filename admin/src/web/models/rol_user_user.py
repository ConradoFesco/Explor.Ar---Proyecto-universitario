from ..extensions import db

class RolUserUser(db.Model):
    __tablename__ = 'Rol_User_User'
    
    Rol_User_id = db.Column(db.Integer, db.ForeignKey('Rol_User.id'), primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    
    def __repr__(self):
        return f'<RolUserUser Rol:{self.Rol_User_id} User:{self.User_id}>'
    
    def to_dict(self):
        return {
            'Rol_User_id': self.Rol_User_id,
            'User_id': self.User_id
        }
