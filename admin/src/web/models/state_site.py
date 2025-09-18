from .. import db

class StateSite(db.Model):
    __tablename__ = 'State_Site'
    
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String)
    deleted = db.Column(db.Boolean, default=False)
    
    # Relaciones
    historic_sites = db.relationship('HistoricSite', backref='state_site', lazy=True)
    
    def __repr__(self):
        return f'<StateSite {self.state}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'state': self.state,
            'deleted': self.deleted
        }
