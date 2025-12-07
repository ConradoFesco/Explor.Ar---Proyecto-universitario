from datetime import datetime
from typing import Any, Dict
from src.web.extensions import db


class HistoricSiteReview(db.Model):
    __tablename__ = 'Historic_Site_Review'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('Historic_Site.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    rejection_reason = db.Column(db.String(200), nullable=True)
    

    user = db.relationship('User', foreign_keys=[user_id], lazy='joined')
  
    def __repr__(self) -> str:
        return f'<HistoricSiteReview site={self.site_id} user={self.user_id} rating={self.rating}>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'site_id': self.site_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'content': self.content,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

