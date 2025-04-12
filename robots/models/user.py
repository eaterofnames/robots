"""
User model for OAuth authentication
"""

from robots.models.base import BaseModel, db

class User(BaseModel):
    """User model for OAuth authentication"""
    __tablename__ = 'users'

    oauth_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    robots = db.relationship('Robot', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>' 