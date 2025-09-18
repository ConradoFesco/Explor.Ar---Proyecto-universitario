from .. import db
from datetime import datetime

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
