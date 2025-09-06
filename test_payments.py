#!/usr/bin/env python3
"""
Quick test to verify payments functionality is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from app import app
from models import Payment, Loan, Customer

def test_payments_api():
    """Test that the payments API is working"""
    with app.app_context():
        try:
            # Test database connection and model
            print("Testing payments table structure...")
            
            # Try to query payments (should work even if empty)
            payments_count = Payment.query.count()
            print(f"✅ Found {payments_count} payments in database")
            
            # Test the query that was failing in the API
            print("Testing payment API query...")
            
            query = db.session.query(Payment)\
                .join(Loan, Payment.loan_id == Loan.id)\
                .join(Customer, Loan.customer_id == Customer.id)
            
            # This should not fail now
            results = query.limit(5).all()
            print(f"✅ Payment API query works! Found {len(results)} payments")
            
            # Check if we have any loans for payment creation
            loans_count = Loan.query.count()
            customers_count = Customer.query.count()
            
            print(f"✅ Database stats:")
            print(f"   - Customers: {customers_count}")
            print(f"   - Loans: {loans_count}")
            print(f"   - Payments: {payments_count}")
            
            if loans_count == 0:
                print("⚠️  Warning: No loans found. You'll need loans to create payments.")
            
            print("✅ All tests passed! Payments functionality should work.")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            raise

if __name__ == "__main__":
    test_payments_api()
