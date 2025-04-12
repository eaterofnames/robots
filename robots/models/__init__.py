"""
Models package initialization
"""

from robots.models.base import db
from robots.models.user import User
from robots.models.robot import Robot
from robots.models.robot_aspect import RobotAspect

__all__ = ['db', 'User', 'Robot', 'RobotAspect']
