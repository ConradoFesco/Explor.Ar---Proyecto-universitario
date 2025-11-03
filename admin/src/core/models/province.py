from src.web.extensions import db
from typing import Dict, Any

class Province(db.Model):
    __tablename__ = 'Province'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    deleted = db.Column(db.Boolean, default=False)
    
    # Relaciones
    cities = db.relationship('City', backref='province', lazy=True)
    
    def __repr__(self) -> str:
        return f'<Province {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'deleted': self.deleted
        }
