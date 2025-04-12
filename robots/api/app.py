"""
Flask application for the Robots API
"""

from flask import Flask
from robots.db import init_db

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from robots.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 