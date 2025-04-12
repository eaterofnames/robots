"""
Robot model for database storage
"""

from robots.models.base import BaseModel, db

class Robot(BaseModel):
    """Robot model for database storage"""
    __tablename__ = 'robots'

    name = db.Column(db.String(255), unique=True, nullable=False)
    model = db.Column(db.String(255), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='idle')
    deployed = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(255), default='no location')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to aspects
    aspects = db.relationship('RobotAspect', backref='robot', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Robot {self.name}>'

    def to_dict(self):
        """Convert robot instance to dictionary"""
        data = {
            "name": self.name,
            "model": self.model,
            "hostname": self.hostname,
            "status": self.status,
            "deployed": self.deployed,
            "location": self.location
        }
        # Add dynamic aspects
        data.update({aspect.name: aspect.value for aspect in self.aspects})
        return data
