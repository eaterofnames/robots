"""
Database initialization
"""

from flask import Flask
from flask_migrate import Migrate
from robots.models.base import db
from robots.db.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

def init_db(app: Flask):
    """Initialize database with Flask app"""
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Create tables
    with app.app_context():
        db.create_all()
