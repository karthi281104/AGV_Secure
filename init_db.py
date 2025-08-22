#!/usr/bin/env python3
"""
Database initialization script for AGV Secure application.
Creates all database tables based on the models.
"""

from app import app
from extensions import db
from models import Customer, Loan, Payment, Employee

def init_database():
    """Initialize the database by creating all tables."""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Print table information
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")

if __name__ == '__main__':
    init_database()