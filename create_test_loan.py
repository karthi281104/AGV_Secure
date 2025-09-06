#!/usr/bin/env python3
"""
Script to create test loan data for payment testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import Customer, Loan
import uuid
from datetime import datetime, timedelta
import decimal

def create_test_loan():
    with app.app_context():
        try:
            # Check if we already have customers and loans
            customer_count = Customer.query.count()
            loan_count = Loan.query.count()
            
            print(f"Current customers: {customer_count}")
            print(f"Current loans: {loan_count}")
            
            if loan_count == 0 and customer_count > 0:
                # Get the first customer to create a test loan
                customer = Customer.query.first()
                
                if customer:
                    print(f"Creating test loan for customer: {customer.name}")
                    
                    # Create a test loan
                    loan = Loan(
                        customer_id=customer.id,
                        loan_number=f"LOAN{loan_count + 1:06d}",
                        principal_amount=decimal.Decimal('50000.00'),
                        interest_rate=decimal.Decimal('12.50'),
                        tenure_months=12,
                        disbursed_date=datetime.utcnow(),
                        maturity_date=datetime.utcnow() + timedelta(days=365),
                        loan_type='gold',
                        status='active'
                    )
                    
                    db.session.add(loan)
                    db.session.commit()
                    
                    print(f"✅ Test loan created: {loan.loan_number}")
                else:
                    print("❌ No customers found to create test loan")
            else:
                print("Loans already exist or no customers available")
                
        except Exception as e:
            print(f"❌ Error creating test loan: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_loan()
