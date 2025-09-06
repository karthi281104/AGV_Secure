#!/usr/bin/env python3
"""
Migration script to fix database schema inconsistencies
Adds missing fields to existing tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("🔧 Starting database schema fixes...")
            
            # Add status column to customers table if it doesn't exist
            try:
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='customers' AND column_name='status'
                """))
                
                if not result.fetchone():
                    print("📝 Adding status column to customers table...")
                    db.session.execute(text("""
                        ALTER TABLE customers 
                        ADD COLUMN status VARCHAR(20) DEFAULT 'active'
                    """))
                    print("✅ Status column added to customers table")
                else:
                    print("⚪ Status column already exists in customers table")
                    
            except Exception as e:
                print(f"⚠️  Error checking/adding status column to customers: {e}")
            
            # Add interest_amount and payment_type columns to payments table
            try:
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='payments' AND column_name='interest_amount'
                """))
                
                if not result.fetchone():
                    print("📝 Adding interest_amount column to payments table...")
                    db.session.execute(text("""
                        ALTER TABLE payments 
                        ADD COLUMN interest_amount NUMERIC(15,2) DEFAULT 0
                    """))
                    print("✅ Interest_amount column added to payments table")
                else:
                    print("⚪ Interest_amount column already exists in payments table")
                    
            except Exception as e:
                print(f"⚠️  Error checking/adding interest_amount column to payments: {e}")
            
            # Add payment_type column to payments table
            try:
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='payments' AND column_name='payment_type'
                """))
                
                if not result.fetchone():
                    print("📝 Adding payment_type column to payments table...")
                    db.session.execute(text("""
                        ALTER TABLE payments 
                        ADD COLUMN payment_type VARCHAR(20) DEFAULT 'principal'
                    """))
                    print("✅ Payment_type column added to payments table")
                else:
                    print("⚪ Payment_type column already exists in payments table")
                    
            except Exception as e:
                print(f"⚠️  Error checking/adding payment_type column to payments: {e}")
            
            # Commit all changes
            db.session.commit()
            print("✅ Database schema migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            return False
        
        return True

if __name__ == '__main__':
    success = run_migration()
    if success:
        print("🎉 All database fixes applied successfully!")
    else:
        print("💥 Migration failed - please check the errors above")
        sys.exit(1)
