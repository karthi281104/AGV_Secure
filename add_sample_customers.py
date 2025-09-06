#!/usr/bin/env python3
"""
Script to add sample customers to the database for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Customer
from datetime import datetime

def add_sample_customers():
    with app.app_context():
        try:
            # Check if customers already exist
            existing_count = Customer.query.count()
            if existing_count > 0:
                print(f"Database already has {existing_count} customers. Skipping sample data creation.")
                return

            # Sample customers data
            customers_data = [
                {
                    'name': 'Rajesh Kumar',
                    'mobile': '9876543210',
                    'father_name': 'Suresh Kumar', 
                    'mother_name': 'Prema Kumar',
                    'address': '123 Main Street, Chennai, Tamil Nadu',
                    'pan_number': 'ABCDE1234F',
                    'aadhar_number': '1234 5678 9012'
                },
                {
                    'name': 'Priya Sharma',
                    'mobile': '9876543211',
                    'father_name': 'Mohan Sharma',
                    'mother_name': 'Sunita Sharma', 
                    'address': '456 Park Avenue, Mumbai, Maharashtra',
                    'pan_number': 'FGHIJ5678K',
                    'aadhar_number': '2345 6789 0123'
                },
                {
                    'name': 'Amit Patel',
                    'mobile': '9876543212',
                    'father_name': 'Kiran Patel',
                    'mother_name': 'Meera Patel',
                    'address': '789 Garden Road, Ahmedabad, Gujarat', 
                    'pan_number': 'KLMNO9012P',
                    'aadhar_number': '3456 7890 1234'
                },
                {
                    'name': 'Anitha Reddy',
                    'mobile': '9876543213',
                    'father_name': 'Venkat Reddy',
                    'mother_name': 'Lakshmi Reddy',
                    'address': '321 Temple Street, Hyderabad, Telangana',
                    'pan_number': 'QRSTU3456V',
                    'aadhar_number': '4567 8901 2345'
                },
                {
                    'name': 'Karthik Nair',
                    'mobile': '9876543214',
                    'father_name': 'Raman Nair',
                    'mother_name': 'Radha Nair',
                    'address': '654 Beach Road, Kochi, Kerala',
                    'pan_number': 'WXYZ7890A',
                    'aadhar_number': '5678 9012 3456'
                }
            ]

            # Create customers
            created_count = 0
            for customer_data in customers_data:
                customer = Customer(**customer_data)
                db.session.add(customer)
                created_count += 1

            # Commit all changes
            db.session.commit()
            print(f"✅ Successfully created {created_count} sample customers!")
            
            # Display created customers
            print("\n📋 Created customers:")
            for customer in Customer.query.all():
                print(f"   • {customer.name} ({customer.mobile})")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample customers: {e}")

if __name__ == "__main__":
    print("🧪 Adding sample customers to database...")
    add_sample_customers()
    print("✨ Done!")
