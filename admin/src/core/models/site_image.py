from src.web.extensions import db
from datetime import datetime
from typing import Dict, Any

class SiteImage(db.Model):
    __tablename__ = 'Site_Image'
    
    id = db.Column(db.Integer, primary_key=True)
    id_site = db.Column(db.Integer, db.ForeignKey('Historic_Site.id'), nullable=False)
    url_publica = db.Column(db.String(500), nullable=False)
    titulo_alt = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    orden = db.Column(db.Integer, nullable=False, default=0)
    es_portada = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con HistoricSite
    historic_site = db.relationship('HistoricSite', backref='images', lazy=True)
    
    def __repr__(self) -> str:
        return f'<SiteImage {self.id} - {self.titulo_alt}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'id_site': self.id_site,
            'url_publica': self.url_publica,
            'titulo_alt': self.titulo_alt,
            'descripcion': self.descripcion,
            'orden': self.orden,
            'es_portada': self.es_portada,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


