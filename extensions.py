"""
Database extensions for the AGV Secure application.
This module contains the SQLAlchemy database instance to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance
db = SQLAlchemy()