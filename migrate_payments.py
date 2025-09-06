#!/usr/bin/env python3
"""
Database Migration Script for Payment Model Updates
This script will update the payments table to match the new Payment model structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from app import app
from models import Payment, Loan, Customer
from datetime import datetime
import decimal

def migrate_payments_table():
    """Migrate the payments table to add missing columns"""
    with app.app_context():
        try:
            # Check if payments table exists and get its current structure
            inspector = db.inspect(db.engine)
            
            if 'payments' not in inspector.get_table_names():
                print("Payments table doesn't exist. Creating all tables...")
                db.create_all()
                print("✅ All tables created successfully!")
                return
            
            # Get current columns
            current_columns = [col['name'] for col in inspector.get_columns('payments')]
            print(f"Current payments table columns: {current_columns}")
            
            # Define required columns with their SQL types
            required_columns = {
                'amount': 'NUMERIC(15, 2) NOT NULL DEFAULT 0',
                'payment_date': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
                'payment_method': 'VARCHAR(50) NOT NULL DEFAULT \'cash\'',
                'transaction_id': 'VARCHAR(100)',
                'notes': 'TEXT',
                'created_at': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP'
            }
            
            # Add missing columns
            missing_columns = []
            for col_name, col_def in required_columns.items():
                if col_name not in current_columns:
                    missing_columns.append(f"ADD COLUMN {col_name} {col_def}")
            
            if missing_columns:
                print(f"Adding missing columns: {[col.split()[2] for col in missing_columns]}")
                
                # Execute ALTER TABLE statements
                for alter_stmt in missing_columns:
                    sql = f"ALTER TABLE payments {alter_stmt}"
                    print(f"Executing: {sql}")
                    db.session.execute(db.text(sql))
                
                db.session.commit()
                print("✅ Missing columns added successfully!")
            else:
                print("✅ All required columns already exist!")
                
            # Update existing records with default values if needed
            update_existing_records()
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            raise

def update_existing_records():
    """Update existing payment records with default values for new columns"""
    try:
        # Get all payments that might need updating
        payments = db.session.execute(db.text("SELECT id, payment_number FROM payments")).fetchall()
        
        if payments:
            print(f"Found {len(payments)} existing payment records to update...")
            
            # Update records that have NULL values in new columns
            update_sql = """
                UPDATE payments 
                SET 
                    amount = CASE WHEN amount IS NULL THEN 0 ELSE amount END,
                    payment_date = CASE WHEN payment_date IS NULL THEN CURRENT_TIMESTAMP ELSE payment_date END,
                    payment_method = CASE WHEN payment_method IS NULL THEN 'cash' ELSE payment_method END,
                    created_at = CASE WHEN created_at IS NULL THEN CURRENT_TIMESTAMP ELSE created_at END
                WHERE 
                    amount IS NULL OR 
                    payment_date IS NULL OR 
                    payment_method IS NULL OR 
                    created_at IS NULL
            """
            
            result = db.session.execute(db.text(update_sql))
            db.session.commit()
            
            print(f"✅ Updated {result.rowcount} payment records with default values!")
        else:
            print("ℹ️ No existing payment records found.")
            
    except Exception as e:
        print(f"❌ Error updating existing records: {e}")
        db.session.rollback()
        raise

def create_sample_payment():
    """Create a sample payment record for testing"""
    try:
        # Check if we have any loans to create payments for
        loan = Loan.query.first()
        if not loan:
            print("ℹ️ No loans found. Cannot create sample payment.")
            return
            
        # Check if we already have payments
        existing_payments = Payment.query.count()
        if existing_payments > 0:
            print(f"ℹ️ Found {existing_payments} existing payments. Not creating sample payment.")
            return
        
        # Create a sample payment
        sample_payment = Payment(
            loan_id=loan.id,
            payment_number="PAY000001",
            amount=decimal.Decimal("5000.00"),
            payment_date=datetime.now(),
            payment_method="cash",
            notes="Sample payment for testing"
        )
        
        db.session.add(sample_payment)
        db.session.commit()
        
        print("✅ Sample payment created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample payment: {e}")
        db.session.rollback()

def main():
    print("🔄 Starting Payment Model Migration...")
    print("=" * 50)
    
    with app.app_context():
        migrate_payments_table()
        create_sample_payment()
    
    print("=" * 50)
    print("✅ Migration completed successfully!")
    print("You can now use the payments functionality.")

if __name__ == "__main__":
    main()
