"""
API routes for the Robots application
"""

from flask import Blueprint, jsonify
from robots.models.base import db
from robots.models.robot import Robot
from robots.models.user import User

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@api_bp.route('/test-db')
def test_db():
    """Test database connection and models"""
    try:
        # Try to create a test user
        user = User(
            oauth_id='test123',
            email='test@example.com',
            name='Test User'
        )
        db.session.add(user)
        db.session.commit()
        
        # Try to create a test robot
        robot = Robot(
            name='test-robot',
            model='test-model',
            hostname='test-hostname',
            user_id=user.id
        )
        db.session.add(robot)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Database test successful',
            'user_id': user.id,
            'robot_id': robot.id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 