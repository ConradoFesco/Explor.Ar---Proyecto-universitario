from .. import db
from datetime import datetime

class Tag(db.Model):
    __tablename__ = 'Tag'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)
    
    # Relaciones
    tag_historic_sites = db.relationship('TagHistoricSite', backref='tag', lazy=True)
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deleted': self.deleted
        }
