#!/usr/bin/env python3
"""
Check customers in database
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    from models import Customer
    from extensions import db
    
    with app.app_context():
        try:
            total_customers = Customer.query.count()
            print(f"Total customers in database: {total_customers}")
            
            if total_customers > 0:
                print("\nFirst 10 customers:")
                customers = Customer.query.limit(10).all()
                for customer in customers:
                    print(f"ID: {customer.id}")
                    print(f"Name: {customer.name}")
                    print(f"Mobile: {customer.mobile}")
                    print(f"Email: {customer.email}")
                    print(f"Address: {customer.address}")
                    print("-" * 40)
            else:
                print("No customers found in database!")
                print("You may need to add some customers first.")
                
        except Exception as e:
            print(f"Database error: {e}")
            print("Database might not be initialized or accessible.")
            
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are installed.")
except Exception as e:
    print(f"Error: {e}")
