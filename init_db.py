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
        try:
            # Drop all tables (optional - only if you want to start fresh)
            # db.drop_all()

            # Create all tables
            db.create_all()
            print("Database tables created successfully!")

            # Print table information
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {', '.join(tables)}")

            # Verify employees table exists
            if 'employees' in tables:
                print("✅ Employees table created successfully!")
            else:
                print("❌ Employees table was not created!")

        except Exception as e:
            print(f"Error creating database tables: {e}")


if __name__ == '__main__':
    init_database()