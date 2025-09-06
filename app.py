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
from datetime import datetime, timedelta
import base64
import uuid
import random
import string
import decimal
from sqlalchemy import or_, func
from dateutil.relativedelta import relativedelta

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# --- DATABASE CONFIGURATION ---
# Assumes you have a config.py file or set the URI directly
app.config.from_object('config.Config')

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

# FIXED: Add allowed file extensions for security
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_upload(file, max_size_mb=5):
    """Validate file upload with security checks"""
    if not file or not file.filename:
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Additional validation can be added here (virus scanning, etc.)
    return True, "File is valid"

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
    try:
        token = oauth.auth0.authorize_access_token()
        
        # Validate token
        if not token:
            flash("Authentication failed. Please try again.", "error")
            return redirect("/login")
        
        # Store user profile
        session["profile"] = token
        
        # Get next URL or default to dashboard
        next_url = session.pop('next_url', None)
        
        flash("Login successful!", "success")
        return redirect(next_url or "/dashboard")
        
    except Exception as e:
        # Log the error for debugging
        print(f"Authentication error: {e}")
        flash("Authentication failed. Please try again.", "error")
        return redirect("/login")


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


@app.route("/customers/edit/<customer_id>")
@requires_auth
def edit_customer(customer_id):
    """Edit customer page"""
    from models import Customer
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            flash("Customer not found", "error")
            return redirect(url_for('customers'))
        
        return render_template("edit_customer.html", customer=customer, userinfo=session.get('profile'))
    except Exception as e:
        flash(f"Error loading customer: {e}", "error")
        return redirect(url_for('customers'))


@app.route("/customers/update/<customer_id>", methods=["POST"])
@requires_auth
def update_customer(customer_id):
    """Update customer information"""
    from models import Customer, db
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            flash("Customer not found", "error")
            return redirect(url_for('customers'))
        
        # Update customer fields
        customer.name = request.form.get('name')
        customer.mobile = request.form.get('mobile')
        customer.additional_mobile = request.form.get('additional_mobile')
        customer.father_name = request.form.get('father_name')
        customer.mother_name = request.form.get('mother_name')
        customer.email = request.form.get('email')
        customer.address = request.form.get('address')
        customer.pan_number = request.form.get('pan_number')
        customer.aadhar_number = request.form.get('aadhar_number')
        
        db.session.commit()
        flash("Customer updated successfully!", "success")
        return redirect(url_for('customers'))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating customer: {e}", "error")
        return redirect(url_for('customers'))


@app.route("/customers/create", methods=["POST"])
@requires_auth
def create_customer():
    """Create new customer"""
    from models import Customer, db
    from validators import CustomerValidator

    try:
        # Get form data
        form_data = {
            'name': request.form.get('name'),
            'mobile': request.form.get('mobile'),
            'additional_mobile': request.form.get('additional_mobile'),
            'father_name': request.form.get('father_name'),
            'mother_name': request.form.get('mother_name'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'pan_number': request.form.get('pan_number'),
            'aadhar_number': request.form.get('aadhar_number'),
            'fingerprint_data': request.form.get('fingerprint_data')
        }

        # FIXED: Validate customer data using validator
        is_valid, validation_errors = CustomerValidator.validate_customer_data(form_data)
        if not is_valid:
            for field, error in validation_errors.items():
                flash(f"{field.replace('_', ' ').title()}: {error}", "error")
            return redirect(url_for('add_customer'))

        # Handle file uploads with validation - FIXED
        pan_photo = request.files.get('pan_photo')
        aadhar_photo = request.files.get('aadhar_photo')

        pan_photo_url = None
        aadhar_photo_url = None
        document_metadata = {}

        if pan_photo and pan_photo.filename:
            # Validate file
            is_valid, error_msg = validate_file_upload(pan_photo)
            if not is_valid:
                flash(f"PAN photo error: {error_msg}", "error")
                return redirect(url_for('add_customer'))
                
            filename = secure_filename(f"pan_{form_data['name']}_{pan_photo.filename}")
            pan_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pan_photo.save(pan_photo_path)
            pan_photo_url = f"uploads/{filename}"
            document_metadata["pan_document"] = {
                "filename": filename,
                "original_name": pan_photo.filename,
                "upload_date": str(datetime.now()),
                "file_size": os.path.getsize(pan_photo_path)
            }

        if aadhar_photo and aadhar_photo.filename:
            # Validate file
            is_valid, error_msg = validate_file_upload(aadhar_photo)
            if not is_valid:
                flash(f"Aadhar photo error: {error_msg}", "error")
                return redirect(url_for('add_customer'))
                
            filename = secure_filename(f"aadhar_{form_data['name']}_{aadhar_photo.filename}")
            aadhar_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            aadhar_photo.save(aadhar_photo_path)
            aadhar_photo_url = f"uploads/{filename}"
            document_metadata["aadhar_document"] = {
                "filename": filename,
                "original_name": aadhar_photo.filename,
                "upload_date": str(datetime.now()),
                "file_size": os.path.getsize(aadhar_photo_path)
            }

        # Create new customer with validated data
        new_customer = Customer(
            name=form_data['name'],
            mobile=form_data['mobile'],
            additional_mobile=form_data['additional_mobile'],
            father_name=form_data['father_name'],
            mother_name=form_data['mother_name'],
            email=form_data['email'],
            address=form_data['address'],
            pan_number=form_data['pan_number'],
            aadhar_number=form_data['aadhar_number'],
            pan_photo_url=pan_photo_url,
            aadhar_photo_url=aadhar_photo_url,
            document_metadata=json.dumps(document_metadata) if document_metadata else None,
            fingerprint_data=form_data['fingerprint_data']
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
    return render_template("reports.html", userinfo=session.get('profile'))


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


@app.route("/api/customers")
@requires_auth
def api_customers():
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
                "email": customer.email,
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


@app.route("/api/customers/<customer_id>")
@requires_auth
def api_customer_details(customer_id):
    """API endpoint to get detailed customer information"""
    from models import Customer
    
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        customer_data = {
            "id": str(customer.id),
            "name": customer.name,
            "mobile": customer.mobile,
            "additional_mobile": customer.additional_mobile,
            "father_name": customer.father_name,
            "mother_name": customer.mother_name,
            "email": customer.email,
            "address": customer.address,
            "aadhar_number": customer.aadhar_number,
            "pan_number": customer.pan_number,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
            "loans": [
                {
                    "id": str(loan.id),
                    "amount": float(loan.amount),
                    "status": loan.status,
                    "created_at": loan.created_at.isoformat() if loan.created_at else None
                } for loan in customer.loans
            ] if customer.loans else []
        }
        
        return jsonify(customer_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customers/<customer_id>", methods=["DELETE"])
@requires_auth
def api_delete_customer(customer_id):
    """API endpoint to delete a customer"""
    from models import Customer, db
    
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Check if customer has active loans
        if customer.loans:
            return jsonify({"error": "Cannot delete customer with active loans"}), 400
        
        # Delete the customer
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Customer deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/loans/search-customer")
@requires_auth
def loans_search_customer():
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
        # Get customer ID and validate
        customer_id = request.form.get('customer_id')
        if not customer_id:
            flash("Customer selection is required", "danger")
            return redirect(url_for('new_loan'))

        # Validate customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            flash("Selected customer not found", "danger")
            return redirect(url_for('new_loan'))

        # Get and validate form data
        principal_amount = request.form.get('principal_amount')
        interest_rate = request.form.get('interest_rate')
        tenure_months = request.form.get('tenure_months')
        loan_type = request.form.get('loan_type')

        # FIXED: Add validation for required fields
        if not all([principal_amount, interest_rate, tenure_months, loan_type]):
            flash("All loan details are required", "danger")
            return redirect(url_for('new_loan'))

        # FIXED: Validate numeric values
        try:
            principal_amount = decimal.Decimal(str(principal_amount))
            interest_rate = decimal.Decimal(str(interest_rate))
            tenure_months = int(tenure_months)
            
            if principal_amount <= 0:
                flash("Principal amount must be greater than zero", "danger")
                return redirect(url_for('new_loan'))
            
            if interest_rate <= 0 or interest_rate > 100:
                flash("Interest rate must be between 0 and 100", "danger")
                return redirect(url_for('new_loan'))
            
            if tenure_months <= 0 or tenure_months > 360:  # Max 30 years
                flash("Tenure must be between 1 and 360 months", "danger")
                return redirect(url_for('new_loan'))
                
        except (ValueError, decimal.InvalidOperation):
            flash("Invalid numeric values provided", "danger")
            return redirect(url_for('new_loan'))

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
        
        # Calculate actual monthly data from the last 6 months
        monthly_data = []
        for i in range(6, 0, -1):
            month_start = datetime.utcnow().replace(day=1) - relativedelta(months=i-1)
            month_end = month_start + relativedelta(months=1) - relativedelta(days=1)
            
            month_disbursed = db.session.query(db.func.sum(Loan.principal_amount)).filter(
                Loan.disbursed_date >= month_start,
                Loan.disbursed_date <= month_end
            ).scalar() or 0
            
            monthly_data.append({
                'month': 7-i,
                'amount': float(month_disbursed)
            })
        
        # Calculate actual loan types distribution
        loan_types = []
        for loan_type in ['gold', 'personal', 'business', 'vehicle']:
            count = db.session.query(Loan).filter(Loan.loan_type == loan_type).count()
            percentage = (count / total_loans * 100) if total_loans > 0 else 0
            loan_types.append({
                'type': f'{loan_type.title()} Loans',
                'count': count,
                'percentage': round(percentage, 1)
            })
        
        # Get actual recent loans (latest 5)
        recent_loans = []
        loans_query = db.session.query(Loan, Customer).join(Customer).order_by(Loan.disbursed_date.desc()).limit(5).all()
        for loan, customer in loans_query:
            recent_loans.append({
                'id': loan.loan_number,
                'customer': customer.name,
                'amount': float(loan.principal_amount),
                'type': loan.loan_type.title(),
                'date': loan.disbursed_date.isoformat() if loan.disbursed_date else datetime.utcnow().isoformat()
            })
        
        # For payments, we would need a Payment model - for now return empty
        recent_payments = []
        
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
        # Return minimal data structure in case of database issues
        return jsonify({
            'total_customers': 0,
            'total_disbursed': 0,
            'total_interest': 0,
            'active_loans': 0,
            'customers_change': 0,
            'disbursed_change': 0,
            'interest_change': 0,
            'loans_change': 0,
            'monthlyData': [],
            'loanTypes': [],
            'recentLoans': [],
            'recentPayments': []
        }), 500


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


# Reports API Endpoints
@app.route("/api/reports/metrics")
@requires_auth
def api_reports_metrics():
    """API endpoint to get key performance metrics for reports"""
    try:
        from models import Customer, Loan
        from sqlalchemy import func, extract
        from datetime import datetime, timedelta
        
        # Get date range from query parameters
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        
        # Calculate total loans amount
        loans_query = Loan.query
        if from_date and to_date:
            loans_query = loans_query.filter(
                Loan.disbursed_date >= from_date,
                Loan.disbursed_date <= to_date
            )
        
        total_loans_amount = db.session.query(func.sum(Loan.principal_amount)).scalar() or 0
        
        # Calculate total customers
        customers_query = Customer.query
        if from_date and to_date:
            customers_query = customers_query.filter(
                Customer.created_at >= from_date,
                Customer.created_at <= to_date
            )
        
        total_customers = customers_query.count()
        
        # Calculate average interest rate
        avg_interest = db.session.query(func.avg(Loan.interest_rate)).scalar() or 0
        
        # Calculate monthly growth (mock calculation)
        monthly_growth = 12.5  # This could be calculated based on historical data
        
        return jsonify({
            'totalLoansAmount': float(total_loans_amount),
            'totalCustomers': total_customers,
            'averageInterest': float(avg_interest),
            'monthlyGrowth': monthly_growth,
            'loansGrowth': 15.2,
            'customersGrowth': 8.7,
            'interestChange': -0.2,
            'growthChange': 2.1
        })
        
    except Exception as e:
        print(f"Error in reports metrics: {e}")
        return jsonify({
            'totalLoansAmount': 0,
            'totalCustomers': 0,
            'averageInterest': 0,
            'monthlyGrowth': 0
        }), 500


@app.route("/api/reports/charts")
@requires_auth
def api_reports_charts():
    """API endpoint to get chart data for reports"""
    try:
        from models import Loan
        from sqlalchemy import func, extract
        from datetime import datetime, timedelta
        
        # Get date range
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        
        # Loan trend data (monthly aggregation)
        loan_trend = []
        if from_date and to_date:
            trend_query = db.session.query(
                func.date_trunc('month', Loan.disbursed_date).label('month'),
                func.sum(Loan.principal_amount).label('total_amount')
            ).filter(
                Loan.disbursed_date >= from_date,
                Loan.disbursed_date <= to_date
            ).group_by(
                func.date_trunc('month', Loan.disbursed_date)
            ).all()
            
            for row in trend_query:
                loan_trend.append({
                    'date': row.month.strftime('%Y-%m'),
                    'amount': float(row.total_amount or 0)
                })
        
        # Loan types distribution
        loan_types_query = db.session.query(
            Loan.loan_type,
            func.count(Loan.id).label('count'),
            func.sum(Loan.principal_amount).label('total_amount')
        ).group_by(Loan.loan_type).all()
        
        loan_types = []
        for row in loan_types_query:
            loan_types.append({
                'type': row.loan_type or 'Unknown',
                'count': row.count,
                'amount': float(row.total_amount or 0)
            })
        
        return jsonify({
            'loanTrend': loan_trend,
            'loanTypes': loan_types,
            'financialOverview': []  # This could be expanded with more complex calculations
        })
        
    except Exception as e:
        print(f"Error in reports charts: {e}")
        return jsonify({
            'loanTrend': [],
            'loanTypes': [],
            'financialOverview': []
        }), 500


@app.route("/api/reports/loans-summary")
@requires_auth
def api_reports_loans_summary():
    """API endpoint to get loans summary for reports table"""
    try:
        from models import Customer, Loan
        
        loans = db.session.query(Loan, Customer).join(
            Customer, Loan.customer_id == Customer.id
        ).order_by(Loan.disbursed_date.desc()).limit(50).all()
        
        loans_data = []
        for loan, customer in loans:
            loans_data.append({
                'id': str(loan.id),
                'loan_number': loan.loan_number,
                'customer_name': customer.name,
                'customer_mobile': customer.mobile,
                'principal_amount': float(loan.principal_amount),
                'interest_rate': float(loan.interest_rate),
                'tenure_months': loan.tenure_months,
                'disbursed_date': loan.disbursed_date.isoformat(),
                'status': 'Active'  # You could add a status field to the Loan model
            })
        
        return jsonify(loans_data)
        
    except Exception as e:
        print(f"Error in loans summary: {e}")
        return jsonify([]), 500


@app.route("/api/reports/customer-analysis")
@requires_auth
def api_reports_customer_analysis():
    """API endpoint to get customer analysis data"""
    try:
        from models import Customer, Loan
        from sqlalchemy import func
        
        # Customer statistics with loan aggregations
        customer_stats = db.session.query(
            Customer.id,
            Customer.name,
            Customer.mobile,
            func.count(Loan.id).label('total_loans'),
            func.sum(Loan.principal_amount).label('total_amount'),
            func.max(Loan.disbursed_date).label('last_loan_date')
        ).outerjoin(Loan).group_by(Customer.id, Customer.name, Customer.mobile).all()
        
        customers_data = []
        for row in customer_stats:
            customers_data.append({
                'id': str(row.id),
                'name': row.name,
                'mobile': row.mobile,
                'total_loans': row.total_loans or 0,
                'total_amount': float(row.total_amount or 0),
                'last_loan_date': row.last_loan_date.isoformat() if row.last_loan_date else None,
                'credit_score': 750,  # Mock credit score
                'status': 'Active'
            })
        
        # Summary stats
        total_customers = Customer.query.count()
        new_customers = Customer.query.filter(
            Customer.created_at >= datetime.now() - timedelta(days=30)
        ).count()
        active_customers = db.session.query(Customer).join(Loan).distinct().count()
        avg_loan_size = db.session.query(func.avg(Loan.principal_amount)).scalar() or 0
        
        return jsonify({
            'customers': customers_data[:20],  # Limit to 20 for display
            'stats': {
                'newCustomers': new_customers,
                'activeCustomers': active_customers,
                'averageLoanSize': float(avg_loan_size)
            }
        })
        
    except Exception as e:
        print(f"Error in customer analysis: {e}")
        return jsonify({
            'customers': [],
            'stats': {'newCustomers': 0, 'activeCustomers': 0, 'averageLoanSize': 0}
        }), 500


@app.route("/api/reports/performance-metrics")
@requires_auth
def api_reports_performance_metrics():
    """API endpoint to get performance metrics"""
    try:
        from models import Loan
        
        # Calculate portfolio value
        total_portfolio = db.session.query(func.sum(Loan.principal_amount)).scalar() or 0
        
        # Mock metrics - these could be calculated from actual data
        total_portfolio_float = float(total_portfolio)
        metrics = {
            'approvalRate': 87.5,
            'processingTime': 2.8,
            'satisfaction': 94.2,
            'defaultRate': 1.8,
            'totalPortfolio': total_portfolio_float,
            'totalInterest': total_portfolio_float * 0.15,  # Assume 15% interest earned
            'outstandingAmount': total_portfolio_float * 0.8,  # Assume 80% still outstanding
            'collectionRate': 92.3
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        print(f"Error in performance metrics: {e}")
        return jsonify({
            'approvalRate': 0, 'processingTime': 0, 'satisfaction': 0,
            'defaultRate': 0, 'totalPortfolio': 0, 'totalInterest': 0,
            'outstandingAmount': 0, 'collectionRate': 0
        }), 500


# Payments Routes
@app.route('/payments')
@requires_auth
def payments():
    """Payments management page"""
    return render_template(
        "payments.html",
        userinfo=session.get('profile')
    )


@app.route('/api/payments')
@requires_auth
def api_payments():
    """API endpoint to get all payments with pagination and search"""
    from models import Payment, Loan, Customer
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_query = request.args.get('q', '')
    loan_id = request.args.get('loan_id', '')
    
    try:
        # Base query with joins
        query = db.session.query(Payment)\
            .join(Loan, Payment.loan_id == Loan.id)\
            .join(Customer, Loan.customer_id == Customer.id)
        
        # Apply search filter if provided
        if search_query and len(search_query) >= 3:
            query = query.filter(
                or_(
                    Payment.payment_number.ilike(f"%{search_query}%"),
                    Customer.name.ilike(f"%{search_query}%"),
                    Customer.mobile.ilike(f"%{search_query}%"),
                    Payment.transaction_id.ilike(f"%{search_query}%")
                )
            )
        
        # Filter by loan if provided
        if loan_id:
            query = query.filter(Payment.loan_id == loan_id)
        
        # Order by payment date (newest first)
        query = query.order_by(Payment.payment_date.desc())
        
        # Paginate
        payments_pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        payments = payments_pagination.items
        
        results = []
        for payment in payments:
            results.append({
                "id": str(payment.id),
                "payment_number": payment.payment_number,
                "amount": float(payment.amount),
                "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "payment_method": payment.payment_method,
                "transaction_id": payment.transaction_id,
                "notes": payment.notes,
                "loan": {
                    "id": str(payment.loan.id),
                    "loan_number": payment.loan.loan_number,
                    "customer_name": payment.loan.customer.name,
                    "customer_mobile": payment.loan.customer.mobile
                },
                "created_at": payment.created_at.isoformat() if payment.created_at else None
            })

        return jsonify({
            "payments": results,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": payments_pagination.total,
                "pages": payments_pagination.pages,
                "has_next": payments_pagination.has_next,
                "has_prev": payments_pagination.has_prev
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/payments/<payment_id>')
@requires_auth
def api_payment_detail(payment_id):
    """API endpoint to get payment details"""
    from models import Payment
    
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        return jsonify({
            "id": str(payment.id),
            "payment_number": payment.payment_number,
            "amount": float(payment.amount),
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "payment_method": payment.payment_method,
            "transaction_id": payment.transaction_id,
            "notes": payment.notes,
            "loan": {
                "id": str(payment.loan.id),
                "loan_number": payment.loan.loan_number,
                "customer_name": payment.loan.customer.name,
                "customer_mobile": payment.loan.customer.mobile,
                "principal_amount": float(payment.loan.principal_amount)
            },
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "updated_at": payment.updated_at.isoformat() if payment.updated_at else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/payments/new')
@requires_auth
def new_payment():
    """New payment recording page"""
    return render_template(
        "new_payment.html",
        userinfo=session.get('profile')
    )


@app.route('/api/payments', methods=['POST'])
@requires_auth
def create_payment():
    """API endpoint to create a new payment"""
    from models import Payment, Loan
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['loan_id', 'amount', 'payment_date', 'payment_method']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Verify loan exists
        loan = Loan.query.get(data['loan_id'])
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
        
        # FIXED: Validate amount
        try:
            amount = decimal.Decimal(str(data['amount']))
            if amount <= 0:
                return jsonify({"error": "Payment amount must be greater than zero"}), 400
        except (ValueError, decimal.InvalidOperation):
            return jsonify({"error": "Invalid payment amount"}), 400
        
        # Generate payment number
        payment_count = Payment.query.count() + 1
        payment_number = f"PAY{payment_count:06d}"
        
        # FIXED: Parse interest amount and payment type
        interest_amount = decimal.Decimal(str(data.get('interest_amount', 0)))
        payment_type = data.get('payment_type', 'principal')
        
        # FIXED: Validate payment date
        try:
            payment_date = datetime.fromisoformat(data['payment_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid payment date format"}), 400
        
        # Create payment
        payment = Payment(
            loan_id=data['loan_id'],
            payment_number=payment_number,
            amount=amount,
            payment_date=payment_date,
            payment_method=data['payment_method'],
            transaction_id=data.get('transaction_id'),
            notes=data.get('notes'),
            interest_amount=interest_amount,
            payment_type=payment_type
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            "message": "Payment recorded successfully",
            "payment": {
                "id": str(payment.id),
                "payment_number": payment.payment_number,
                "amount": float(payment.amount),
                "interest_amount": float(payment.interest_amount),
                "payment_type": payment.payment_type
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/loans/search')
@requires_auth
def api_loans_search():
    """API endpoint to search for loans (for payment forms)"""
    from models import Loan, Customer
    
    query = request.args.get('q', '')
    
    if not query or len(query) < 3:
        return jsonify({"loans": []})
    
    try:
        loans = db.session.query(Loan)\
            .join(Customer, Loan.customer_id == Customer.id)\
            .filter(
                or_(
                    Loan.loan_number.ilike(f"%{query}%"),
                    Customer.name.ilike(f"%{query}%"),
                    Customer.mobile.ilike(f"%{query}%")
                )
            )\
            .limit(10)\
            .all()
        
        results = []
        for loan in loans:
            results.append({
                "id": str(loan.id),
                "loan_number": loan.loan_number,
                "customer_name": loan.customer.name,
                "customer_mobile": loan.customer.mobile,
                "principal_amount": float(loan.principal_amount),
                "status": loan.status
            })
        
        return jsonify({"loans": results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)