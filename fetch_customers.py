# fetch_customers.py

from app import app  # Import the Flask app instance from your app.py file
from models import db, Customer  # Import the db instance and Customer model from models.py

def get_all_customers():
    """
    Queries the database for all customers and prints their details.
    """
    # The 'with app.app_context()' is crucial. It sets up the
    # necessary environment for your database queries to work,
    # just like they would in a running Flask application.
    with app.app_context():
        try:
            # Use the Customer model to query all records from the 'customers' table
            customers = Customer.query.all()

            if not customers:
                print("No customers found in the database.")
                return

            print("--- Customer List ---")
            # Loop through the results and print the details for each customer
            for customer in customers:
                print(f"ID: {customer.id}, Name: {customer.name}, Email: {customer.email}")
            print("---------------------")

        except Exception as e:
            print(f"An error occurred while connecting to the database or fetching data: {e}")
            print("Please ensure your DATABASE_URL in the .env file is correct and the database is accessible.")

if __name__ == '__main__':
    get_all_customers()