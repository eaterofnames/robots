"""
Database initialization
"""

from flask import Flask
from flask_migrate import Migrate
from robots.models.base import db
import sys

def init_db(app: Flask):
    """Initialize database with Flask app"""
    # Load TOML config based on Python version
    if sys.version_info >= (3, 11):
        import tomllib
        with open('fleet-config.toml', 'rb') as f:
            config = tomllib.load(f)
    else:
        import tomli
        with open('fleet-config.toml', 'rb') as f:
            config = tomli.load(f)

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['SQLALCHEMY_TRACK_MODIFICATIONS']

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Create tables
    with app.app_context():
        db.create_all()
