import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, flash, jsonify
from functools import wraps
from extensions import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
import uuid
import random
import string
from sqlalchemy import or_
from dateutil.relativedelta import relativedelta

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY", "dev-secret-key-for-testing")

# --- DATABASE CONFIGURATION ---
# Simple SQLite configuration for testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- INITIALIZE DATABASE ---
# Initialize the db object with the app
db.init_app(app)
# ----------------------------

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


# Authentication decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            session['next_url'] = request.url
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# Add this configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["profile"] = token
    next_url = session.pop('next_url', None)
    return redirect(next_url or "/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


## PROTECTED ROUTES

@app.route("/test-dashboard")
def test_dashboard():
    """Test dashboard without authentication"""
    return render_template("dashboard.html", userinfo={'name': 'Test User', 'picture': 'https://via.placeholder.com/40'})

@app.route("/dashboard")
@requires_auth
def dashboard():
    return render_template(
        "dashboard.html",
        userinfo=session.get('profile')
    )


@app.route('/calculators/emi')
@requires_auth
def emi():
    return render_template('emi_calculator.html')


@app.route('/calculators/gold')
@requires_auth
def gold():
    return render_template('gold_calculator.html')


@app.route('/calculators/gold_conversion')
@requires_auth
def gold_cov():
    return render_template('gold_conversion.html')


@app.route("/profile")
@requires_auth
def profile():
    return render_template(
        "profile.html",
        userinfo=session['profile']
    )


@app.route("/loans")
@requires_auth
def loans():
    return render_template("loans.html", userinfo=session.get('profile'))


@app.route("/customers")
@requires_auth
def customers():
    """Customer management - requires login"""
    from models import Customer  # Import model here to avoid circular dependency
    try:
        all_customers = Customer.query.all()
    except Exception as e:
        flash(f"Error fetching customers: {e}", "danger")
        all_customers = []
    return render_template("customers.html", customers=all_customers)


@app.route("/customers/add")
@requires_auth
def add_customer():
    """Add new customer page"""
    return render_template("add_customer.html", userinfo=session.get('profile'))


@app.route("/customers/create", methods=["POST"])
@requires_auth
def create_customer():
    """Create new customer"""
    from models import Customer, db

    try:
        # Get form data
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        additional_mobile = request.form.get('additional_mobile')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        address = request.form.get('address')
        pan_number = request.form.get('pan_number')
        aadhar_number = request.form.get('aadhar_number')
        fingerprint_data = request.form.get('fingerprint_data')

        # Handle file uploads
        pan_photo = request.files.get('pan_photo')
        aadhar_photo = request.files.get('aadhar_photo')

        pan_photo_url = None
        aadhar_photo_url = None
        document_metadata = {}

        if pan_photo and pan_photo.filename:
            filename = secure_filename(f"pan_{name}_{pan_photo.filename}")
            pan_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pan_photo.save(pan_photo_path)
            pan_photo_url = f"uploads/{filename}"
            document_metadata["pan_document"] = {
                "filename": filename,
                "original_name": pan_photo.filename,
                "upload_date": str(datetime.now())
            }

        if aadhar_photo and aadhar_photo.filename:
            filename = secure_filename(f"aadhar_{name}_{aadhar_photo.filename}")
            aadhar_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            aadhar_photo.save(aadhar_photo_path)
            aadhar_photo_url = f"uploads/{filename}"
            document_metadata["aadhar_document"] = {
                "filename": filename,
                "original_name": aadhar_photo.filename,
                "upload_date": str(datetime.now())
            }

        # Create new customer with corrected field names
        new_customer = Customer(
            name=name,
            mobile=mobile,
            additional_mobile=additional_mobile,
            father_name=father_name,
            mother_name=mother_name,
            address=address,
            pan_number=pan_number,
            aadhar_number=aadhar_number,
            pan_photo_url=pan_photo_url,  # Changed from pan_photo_path
            aadhar_photo_url=aadhar_photo_url,  # Changed from aadhar_photo_path
            document_metadata=json.dumps(document_metadata) if document_metadata else None,
            fingerprint_data=fingerprint_data
        )

        db.session.add(new_customer)
        db.session.commit()

        flash("Customer added successfully!", "success")
        return redirect(url_for('customers'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding customer: {str(e)}", "danger")
        return redirect(url_for('add_customer'))


@app.route("/reports")
@requires_auth
def reports():
    return render_template("reports.html")


@app.route("/test-settings")
def test_settings():
    """Test settings page without authentication"""
    return render_template("settings.html", userinfo={'name': 'Test User', 'given_name': 'Test', 'family_name': 'User', 'email': 'test@example.com', 'picture': 'https://via.placeholder.com/150'})

@app.route("/settings")
@requires_auth
def settings():
    """Settings page for user preferences and configuration"""
    return render_template("settings.html", userinfo=session.get('profile'))


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


@app.route("/loans/new")
@requires_auth
def new_loan():
    """New loan page with customer selection"""
    return render_template("new_loan.html", userinfo=session.get('profile'))


@app.route("/test-new-loan")
def test_new_loan():
    """Test new loan page without authentication"""
    return render_template("new_loan.html", userinfo={'name': 'Test User', 'picture': 'https://via.placeholder.com/40'})

@app.route("/test-api/customers")
def test_api_customers():
    """Test API endpoint to get all customers without authentication"""
    from models import Customer
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_query = request.args.get('q', '')
    
    try:
        # Base query
        query = Customer.query
        
        # Apply search filter if provided
        if search_query and len(search_query) >= 3:
            query = query.filter(
                or_(
                    Customer.name.ilike(f"%{search_query}%"),
                    Customer.mobile.ilike(f"%{search_query}%"),
                    Customer.father_name.ilike(f"%{search_query}%"),
                    Customer.aadhar_number.ilike(f"%{search_query}%")
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Customer.created_at.desc())
        
        # Paginate
        customers_pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        customers = customers_pagination.items
        
        results = []
        for customer in customers:
            results.append({
                "id": str(customer.id),
                "name": customer.name,
                "father_name": customer.father_name or "Not provided",
                "mobile": customer.mobile,
                "aadhar_number": customer.aadhar_number or "Not provided",
                "address": customer.address or "Not provided",
                "created_at": customer.created_at.isoformat() if customer.created_at else None
            })

        return jsonify({
            "customers": results,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": customers_pagination.total,
                "pages": customers_pagination.pages,
                "has_next": customers_pagination.has_next,
                "has_prev": customers_pagination.has_prev
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    """API endpoint to get all customers with pagination and search"""
    from models import Customer
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_query = request.args.get('q', '')
    
    try:
        # Base query
        query = Customer.query
        
        # Apply search filter if provided
        if search_query and len(search_query) >= 3:
            query = query.filter(
                or_(
                    Customer.name.ilike(f"%{search_query}%"),
                    Customer.mobile.ilike(f"%{search_query}%"),
                    Customer.father_name.ilike(f"%{search_query}%"),
                    Customer.aadhar_number.ilike(f"%{search_query}%")
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Customer.created_at.desc())
        
        # Paginate
        customers_pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        customers = customers_pagination.items
        
        results = []
        for customer in customers:
            results.append({
                "id": str(customer.id),
                "name": customer.name,
                "father_name": customer.father_name or "Not provided",
                "mobile": customer.mobile,
                "aadhar_number": customer.aadhar_number or "Not provided",
                "address": customer.address or "Not provided",
                "created_at": customer.created_at.isoformat() if customer.created_at else None
            })

        return jsonify({
            "customers": results,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": customers_pagination.total,
                "pages": customers_pagination.pages,
                "has_next": customers_pagination.has_next,
                "has_prev": customers_pagination.has_prev
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test-loans/search-customer")
def test_search_customer():
    """Test API endpoint to search for customers without authentication"""
    from models import Customer
    query = request.args.get('q', '')

    if len(query) < 3:
        return jsonify({"error": "Query must be at least 3 characters"}), 400

    try:
        # Search for customers by name, mobile or father's name
        customers = Customer.query.filter(
            or_(
                Customer.name.ilike(f"%{query}%"),
                Customer.mobile.ilike(f"%{query}%"),
                Customer.father_name.ilike(f"%{query}%")
            )
        ).limit(10).all()

        results = []
        for customer in customers:
            results.append({
                "id": str(customer.id),
                "name": customer.name,
                "father_name": customer.father_name or "Not provided",
                "mobile": customer.mobile,
                "address": customer.address or "Not provided"
            })

        return jsonify({"customers": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    """API endpoint to search for customers (legacy endpoint for compatibility)"""
    from models import Customer
    query = request.args.get('q', '')

    if len(query) < 3:
        return jsonify({"error": "Query must be at least 3 characters"}), 400

    try:
        # Search for customers by name, mobile or father's name
        customers = Customer.query.filter(
            or_(
                Customer.name.ilike(f"%{query}%"),
                Customer.mobile.ilike(f"%{query}%"),
                Customer.father_name.ilike(f"%{query}%")
            )
        ).limit(10).all()

        results = []
        for customer in customers:
            results.append({
                "id": str(customer.id),
                "name": customer.name,
                "father_name": customer.father_name or "Not provided",
                "mobile": customer.mobile,
                "address": customer.address or "Not provided"
            })

        return jsonify({"customers": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/loans/create", methods=["POST"])
@requires_auth
def create_loan():
    """Create a new loan"""
    from models import Customer, Loan

    try:
        # Get customer ID
        customer_id = request.form.get('customer_id')
        if not customer_id:
            flash("Customer selection is required", "danger")
            return redirect(url_for('new_loan'))

        # Get form data
        principal_amount = request.form.get('principal_amount')
        interest_rate = request.form.get('interest_rate')
        tenure_months = request.form.get('tenure_months')
        loan_type = request.form.get('loan_type')

        # Surety information
        surety_name = request.form.get('surety_name')
        surety_mobile = request.form.get('surety_mobile')
        surety_aadhar = request.form.get('surety_aadhar')
        surety_photo = request.files.get('surety_photo')

        # Handle bond paper upload
        bond_paper = request.files.get('bond_paper')
        bond_paper_url = None
        document_urls = {}

        if bond_paper and bond_paper.filename:
            filename = secure_filename(f"bond_{uuid.uuid4()}_{bond_paper.filename}")
            bond_paper_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            bond_paper.save(bond_paper_path)
            bond_paper_url = f"uploads/{filename}"
            document_urls["bond_paper"] = bond_paper_url

        # Handle surety photo upload
        surety_photo_url = None
        if surety_photo and surety_photo.filename:
            filename = secure_filename(f"surety_{uuid.uuid4()}_{surety_photo.filename}")
            surety_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            surety_photo.save(surety_photo_path)
            surety_photo_url = f"uploads/{filename}"
            document_urls["surety_photo"] = surety_photo_url

        # Calculate maturity date
        disbursed_date = datetime.utcnow()
        maturity_date = disbursed_date + relativedelta(months=int(tenure_months))

        # Create loan number - format: GL-YYYYMMDD-XXXX (GL=Gold Loan, followed by date and 4 random digits)
        loan_number_prefix = f"{loan_type[0].upper()}L-{disbursed_date.strftime('%Y%m%d')}"
        random_suffix = ''.join(random.choices(string.digits, k=4))
        loan_number = f"{loan_number_prefix}-{random_suffix}"

        # Store surety details in collateral_details
        collateral_details = {
            "surety": {
                "name": surety_name,
                "mobile": surety_mobile,
                "aadhar": surety_aadhar,
                "photo_url": surety_photo_url
            }
        }

        # Create new loan
        new_loan = Loan(
            customer_id=customer_id,
            loan_number=loan_number,
            principal_amount=principal_amount,
            interest_rate=interest_rate,
            tenure_months=tenure_months,
            disbursed_date=disbursed_date,
            maturity_date=maturity_date,
            loan_type=loan_type,
            collateral_details=collateral_details,
            document_urls=document_urls
        )

        db.session.add(new_loan)
        db.session.commit()

        flash("Loan created successfully!", "success")
        return redirect(url_for('loans'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating loan: {str(e)}", "danger")
        return redirect(url_for('new_loan'))


@app.route("/api/loans")
@requires_auth
def api_loans():
    """API endpoint to get all loans"""
    try:
        # Query loans from the database with customer information
        from models import Loan, Customer  # Import here to avoid circular dependency

        loans_data = db.session.query(Loan, Customer) \
            .join(Customer, Loan.customer_id == Customer.id) \
            .all()

        results = []
        for loan, customer in loans_data:
            # Calculate loan status (in a real app, you would have a proper status field)
            loan_status = "active"
            maturity_date = loan.maturity_date
            current_date = datetime.utcnow()

            if maturity_date and maturity_date < current_date:
                # Loan has passed maturity date
                loan_status = "completed"
            elif loan.disbursed_date > current_date - relativedelta(months=1):
                # Loan was recently created
                loan_status = "pending"

            # Get surety details from collateral_details if available
            surety_name = None
            surety_mobile = None
            surety_aadhar = None
            surety_photo_url = None

            if loan.collateral_details and 'surety' in loan.collateral_details:
                surety = loan.collateral_details['surety']
                surety_name = surety.get('name')
                surety_mobile = surety.get('mobile')
                surety_aadhar = surety.get('aadhar')
                surety_photo_url = surety.get('photo_url')

            # Get bond paper URL from document_urls if available
            bond_paper_url = None
            if loan.document_urls and 'bond_paper' in loan.document_urls:
                bond_paper_url = loan.document_urls['bond_paper']

            # Create loan object
            loan_obj = {
                "id": str(loan.id),
                "loan_number": loan.loan_number,
                "customer_id": str(customer.id),
                "customer_name": customer.name,
                "customer_mobile": customer.mobile,
                "customer_father_name": customer.father_name,
                "customer_address": customer.address,
                "principal_amount": float(loan.principal_amount),
                "interest_rate": float(loan.interest_rate),
                "tenure_months": loan.tenure_months,
                "disbursed_date": loan.disbursed_date.isoformat() if loan.disbursed_date else None,
                "maturity_date": loan.maturity_date.isoformat() if loan.maturity_date else None,
                "loan_type": loan.loan_type,
                "status": loan_status,
                "surety_name": surety_name,
                "surety_mobile": surety_mobile,
                "surety_aadhar": surety_aadhar,
                "surety_photo_url": surety_photo_url,
                "bond_paper_url": bond_paper_url
            }

            results.append(loan_obj)

        return jsonify({"loans": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/dashboard/stats")
@requires_auth
def api_dashboard_stats():
    """API endpoint to get dashboard statistics"""
    try:
        from models import Loan, Customer  # Import here to avoid circular dependency
        
        # Get basic stats
        total_customers = db.session.query(Customer).count()
        total_loans = db.session.query(Loan).count()
        
        # Calculate total disbursed amount
        disbursed_result = db.session.query(db.func.sum(Loan.principal_amount)).scalar()
        total_disbursed = float(disbursed_result) if disbursed_result else 0
        
        # Calculate active loans (loans that are not yet matured)
        active_loans = db.session.query(Loan).filter(
            db.or_(Loan.maturity_date > datetime.utcnow(), Loan.maturity_date.is_(None))
        ).count()
        
        # Calculate estimated interest (this is a simple calculation)
        interest_result = db.session.query(
            db.func.sum(Loan.principal_amount * Loan.interest_rate / 100)
        ).scalar()
        total_interest = float(interest_result) if interest_result else 0
        
        # Sample monthly data (in real app, this would query actual monthly disbursements)
        monthly_data = [
            {'month': i, 'amount': total_disbursed / 6 + (i * 100000)} 
            for i in range(1, 7)
        ]
        
        # Sample loan types distribution
        loan_types = [
            {'type': 'Gold Loans', 'count': int(total_loans * 0.45), 'percentage': 45},
            {'type': 'Personal Loans', 'count': int(total_loans * 0.25), 'percentage': 25},
            {'type': 'Business Loans', 'count': int(total_loans * 0.20), 'percentage': 20},
            {'type': 'Vehicle Loans', 'count': int(total_loans * 0.10), 'percentage': 10}
        ]
        
        # Sample recent activity (latest 5 loans and payments)
        recent_loans = []
        loans_query = db.session.query(Loan, Customer).join(Customer).order_by(Loan.disbursed_date.desc()).limit(5).all()
        for loan, customer in loans_query:
            recent_loans.append({
                'id': loan.loan_number,
                'customer': customer.name,
                'amount': float(loan.principal_amount),
                'type': loan.loan_type.title(),
                'date': loan.disbursed_date.isoformat() if loan.disbursed_date else (datetime.utcnow() - relativedelta(hours=2)).isoformat()
            })
        
        # For payments, we would need a Payment model, so using sample data with recent dates
        recent_payments = [
            {
                'id': 'P001', 
                'customer': 'Sample Customer', 
                'amount': 50000, 
                'loan_id': 'L001', 
                'date': (datetime.utcnow() - relativedelta(hours=1)).isoformat()
            },
            {
                'id': 'P002', 
                'customer': 'Another Customer', 
                'amount': 25000, 
                'loan_id': 'L002', 
                'date': (datetime.utcnow() - relativedelta(hours=3)).isoformat()
            }
        ]
        
        return jsonify({
            'total_customers': total_customers,
            'total_disbursed': total_disbursed,
            'total_interest': total_interest,
            'active_loans': active_loans,
            'customers_change': 12.5,
            'disbursed_change': 8.3,
            'interest_change': 15.2,
            'loans_change': -2.1,
            'monthlyData': monthly_data,
            'loanTypes': loan_types,
            'recentLoans': recent_loans,
            'recentPayments': recent_payments
        })
        
    except Exception as e:
        print(f"Error in dashboard stats: {e}")
        # Return sample data in case of database issues
        return jsonify({
            'total_customers': 1250,
            'total_disbursed': 75000000,
            'total_interest': 12500000,
            'active_loans': 387,
            'customers_change': 12.5,
            'disbursed_change': 8.3,
            'interest_change': 15.2,
            'loans_change': -2.1,
            'monthlyData': [
                {'month': 1, 'amount': 4500000},
                {'month': 2, 'amount': 5200000},
                {'month': 3, 'amount': 4800000},
                {'month': 4, 'amount': 6100000},
                {'month': 5, 'amount': 5800000},
                {'month': 6, 'amount': 7200000}
            ],
            'loanTypes': [
                {'type': 'Gold Loans', 'count': 174, 'percentage': 45},
                {'type': 'Personal Loans', 'count': 97, 'percentage': 25},
                {'type': 'Business Loans', 'count': 77, 'percentage': 20},
                {'type': 'Vehicle Loans', 'count': 39, 'percentage': 10}
            ],
            'recentLoans': [
                {'id': 'L001', 'customer': 'John Doe', 'amount': 500000, 'type': 'Gold', 'date': (datetime.utcnow() - relativedelta(hours=2)).isoformat()},
                {'id': 'L002', 'customer': 'Jane Smith', 'amount': 250000, 'type': 'Personal', 'date': (datetime.utcnow() - relativedelta(hours=5)).isoformat()}
            ],
            'recentPayments': [
                {'id': 'P001', 'customer': 'Alice Johnson', 'amount': 50000, 'loan_id': 'L001', 'date': (datetime.utcnow() - relativedelta(hours=1)).isoformat()},
                {'id': 'P002', 'customer': 'Bob Wilson', 'amount': 25000, 'loan_id': 'L002', 'date': (datetime.utcnow() - relativedelta(hours=4)).isoformat()}
            ]
        })


@app.route("/api/user/profile")
@requires_auth
def api_user_profile():
    """API endpoint to get user profile information"""
    try:
        userinfo = session.get('profile')
        if userinfo:
            return jsonify({
                'name': userinfo.get('name', 'Employee'),
                'role': 'Loan Officer',  # This could be stored in a user profile table
                'email': userinfo.get('email', ''),
                'picture': userinfo.get('picture', ''),
                'avatar': userinfo.get('picture') or f"https://ui-avatars.com/api/?name={userinfo.get('name', 'User')}&background=667eea&color=fff&size=128"
            })
        else:
            return jsonify({
                'name': 'Employee',
                'role': 'Loan Officer',
                'avatar': 'https://ui-avatars.com/api/?name=Employee&background=667eea&color=fff&size=128'
            })
    except Exception as e:
        return jsonify({
            'name': 'Employee', 
            'role': 'Loan Officer',
            'avatar': 'https://ui-avatars.com/api/?name=Employee&background=667eea&color=fff&size=128'
        }), 200


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)