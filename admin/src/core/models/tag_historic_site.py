from src.web.extensions import db
from typing import Dict, Any

class TagHistoricSite(db.Model):
    __tablename__ = 'Tag_Historic_Site'
    
    Tag_id = db.Column(db.Integer, db.ForeignKey('Tag.id'), primary_key=True)
    Historic_Site_id = db.Column(db.Integer, db.ForeignKey('Historic_Site.id'), primary_key=True)
    
    def __repr__(self) -> str:
        return f'<TagHistoricSite Tag:{self.Tag_id} Site:{self.Historic_Site_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'Tag_id': self.Tag_id,
            'Historic_Site_id': self.Historic_Site_id
        }
