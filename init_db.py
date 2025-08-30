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
            print("Starting database initialization...")
            
            # Drop all tables (optional - only if you want to start fresh)
            # Uncomment the next line if you want to recreate all tables
            # db.drop_all()
            # print("Dropped existing tables")

            # Create all tables
            db.create_all()
            print("Database tables created successfully!")

            # Print table information
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {', '.join(tables)}")

            # Verify all expected tables exist
            expected_tables = ['customers', 'loans', 'payments', 'employees']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ {table.capitalize()} table created successfully!")
                else:
                    print(f"❌ {table.capitalize()} table was not created!")

            # Test foreign key constraints by checking table schemas
            for table_name in tables:
                try:
                    columns = inspector.get_columns(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    print(f"Table '{table_name}' has {len(columns)} columns and {len(foreign_keys)} foreign keys")
                except Exception as e:
                    print(f"Warning: Could not inspect table '{table_name}': {e}")

        except Exception as e:
            print(f"Error creating database tables: {e}")
            print(f"Error type: {type(e).__name__}")
            # More detailed error information for debugging
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    init_database()