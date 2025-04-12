"""
RobotAspect model for storing dynamic robot aspects
"""

from robots.models.base import BaseModel, db

class RobotAspect(BaseModel):
    """RobotAspect model for storing dynamic aspects"""
    __tablename__ = 'robot_aspects'

    robot_id = db.Column(db.Integer, db.ForeignKey('robots.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255))

    # Ensure unique aspect names per robot
    __table_args__ = (
        db.UniqueConstraint('robot_id', 'name', name='uix_robot_aspect'),
    )

    def __repr__(self):
        return f'<RobotAspect {self.name}={self.value}>' 