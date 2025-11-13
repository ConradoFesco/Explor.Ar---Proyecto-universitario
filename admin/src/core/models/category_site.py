from src.web.extensions import db
from typing import Dict, Any

class CategorySite(db.Model):
    __tablename__ = 'Category_Site'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    deleted = db.Column(db.Boolean, default=False)
    
    # Relaciones
    historic_sites = db.relationship('HistoricSite', backref='category', lazy=True)
    
    def __repr__(self) -> str:
        return f'<CategorySite {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'deleted': self.deleted
        }
