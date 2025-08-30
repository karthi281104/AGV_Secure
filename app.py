import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, flash
from functools import wraps
from extensions import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import base64

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
    return render_template("loans.html")


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


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)