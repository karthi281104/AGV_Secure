#!/usr/bin/env python3
"""
Migration script to add status column to loans table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def migrate_loans():
    with app.app_context():
        try:
            # Check if status column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'loans' AND column_name = 'status'
            """))
            
            if not result.fetchone():
                print("Adding status column to loans table...")
                
                # Add status column
                db.session.execute(text("""
                    ALTER TABLE loans 
                    ADD COLUMN status VARCHAR(20) DEFAULT 'active'
                """))
                
                # Update existing loans to have active status
                db.session.execute(text("""
                    UPDATE loans 
                    SET status = 'active' 
                    WHERE status IS NULL
                """))
                
                db.session.commit()
                print("✅ Status column added successfully to loans table")
            else:
                print("Status column already exists in loans table")
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_loans()
