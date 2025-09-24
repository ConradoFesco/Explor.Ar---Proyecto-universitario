from ..extensions import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'Event'
    
    id = db.Column(db.Integer, primary_key=True)
    id_site = db.Column(db.Integer, db.ForeignKey('Historic_Site.id'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    type_Action = db.Column(db.String, nullable=False)
    deleted = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Event {self.type_Action} at {self.date_time}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_site': self.id_site,
            'id_user': self.id_user,
            'date_time': self.date_time.isoformat() if self.date_time else None,
            'type_Action': self.type_Action,
            'deleted': self.deleted
        }
