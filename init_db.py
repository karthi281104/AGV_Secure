#!/usr/bin/env python3
"""
Database initialization script for AGV Secure application.
Creates all database tables based on the models.
"""

from app import app
from extensions import db
from models import Customer, Loan, Payment


def init_database():
    """Initialize the database by creating all tables."""
    with app.app_context():
        try:
            print("Starting database initialization...")

            # For development: Drop all tables to recreate with new schema
            print("⚠️  Dropping existing tables to update schema...")
            db.drop_all()
            print("✅ Dropped existing tables")

            # Create all tables with new schema
            db.create_all()
            print("✅ Database tables created successfully!")

            # Print table information
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {', '.join(tables)}")

            # Verify all expected tables exist
            expected_tables = ['customers', 'loans', 'payments']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ {table.capitalize()} table created successfully!")
                else:
                    print(f"❌ {table.capitalize()} table was not created!")

            # Check the new customer table columns
            if 'customers' in tables:
                columns = inspector.get_columns('customers')
                column_names = [col['name'] for col in columns]
                print(f"Customer table columns: {', '.join(column_names)}")

                # Verify new columns exist
                new_columns = ['mobile', 'additional_mobile', 'father_name', 'mother_name',
                               'pan_photo_url', 'aadhar_photo_url', 'document_metadata', 'fingerprint_data']

                for col in new_columns:
                    if col in column_names:
                        print(f"✅ New column '{col}' added successfully!")
                    else:
                        print(f"❌ New column '{col}' missing!")

            # Test foreign key constraints
            for table_name in tables:
                try:
                    columns = inspector.get_columns(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    print(f"Table '{table_name}' has {len(columns)} columns and {len(foreign_keys)} foreign keys")
                except Exception as e:
                    print(f"Warning: Could not inspect table '{table_name}': {e}")

        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    init_database()