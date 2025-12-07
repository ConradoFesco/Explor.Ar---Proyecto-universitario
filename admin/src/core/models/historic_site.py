from src.web.extensions import db
from datetime import datetime
from typing import Dict, Any

class HistoricSite(db.Model):
    __tablename__ = 'Historic_Site'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    brief_description = db.Column(db.Text, nullable=False)
    complete_description = db.Column(db.Text)
    id_ciudad = db.Column(db.Integer, db.ForeignKey('City.id'))
    latitude = db.Column(db.String, nullable=False)
    longitude = db.Column(db.String, nullable=False)
    id_estado = db.Column(db.Integer, db.ForeignKey('State_Site.id'))
    year_inauguration = db.Column(db.Integer)
    id_category = db.Column(db.Integer, db.ForeignKey('Category_Site.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    visible = db.Column(db.Boolean, nullable=False)
    
    events = db.relationship('Event', backref='historic_site', lazy=True)
    tag_historic_sites = db.relationship('TagHistoricSite', backref='historic_site', lazy=True)
    reviews = db.relationship('HistoricSiteReview', backref='site', lazy='joined')
    favorites = db.relationship('FavoriteSite', backref='site', lazy=True)
    
    def __repr__(self) -> str:
        return f'<HistoricSite {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'brief_description': self.brief_description,
            'complete_description': self.complete_description,
            'id_ciudad': self.id_ciudad,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'id_estado': self.id_estado,
            'year_inauguration': self.year_inauguration,
            'id_category': self.id_category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deleted': self.deleted,
            'visible': self.visible
        }
