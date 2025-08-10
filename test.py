from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy
db = SQLAlchemy()
db.init_app(app)


def test_connection():
    with app.app_context():
        try:
            # Test connection with proper text() declaration
            result = db.session.execute(text('SELECT 1 as test'))
            test_value = result.scalar()
            print(f"✅ Database connection successful! Test result: {test_value}")

            # Test basic query
            db_version = db.session.execute(text('SELECT version()')).scalar()
            print(f"✅ PostgreSQL version: {db_version}")

            # Import models after db initialization
            from models import Customer, Loan, Payment, Employee

            # Test table creation
            db.create_all()
            print("✅ Tables created successfully!")

            # Test a simple count query
            customer_count = db.session.execute(text('SELECT COUNT(*) FROM customers')).scalar()
            print(f"✅ Current customers in database: {customer_count}")

            return True

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("📋 Troubleshooting steps:")
            print("1. Check your .env file has correct DATABASE_URL")
            print("2. Verify Supabase credentials are correct")
            print("3. Ensure your Supabase project is running")
            return False


if __name__ == '__main__':
    test_connection()