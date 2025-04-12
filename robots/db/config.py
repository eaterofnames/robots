"""
Database configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    'postgresql://robots:robots@localhost:5432/robots'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False 