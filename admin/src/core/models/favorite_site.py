from datetime import datetime
from src.web.extensions import db


class FavoriteSite(db.Model):
    __tablename__ = 'Favorite_Site'

    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('Historic_Site.id'), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<FavoriteSite user={self.user_id} site={self.site_id}>'

    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'site_id': self.site_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

