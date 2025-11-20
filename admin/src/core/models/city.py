from src.web.extensions import db
from typing import Dict, Any

class City(db.Model):
    __tablename__ = 'City'
    
    id = db.Column(db.Integer, primary_key=True)
    id_province = db.Column(db.Integer, db.ForeignKey('Province.id'))
    name = db.Column(db.String)
    deleted = db.Column(db.Boolean, default=False)
    
    # Relaciones
    historic_sites = db.relationship('HistoricSite', backref='city', lazy=True)
    
    def __repr__(self) -> str:
        return f'<City {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'id_province': self.id_province,
            'name': self.name,
            'deleted': self.deleted
        }
