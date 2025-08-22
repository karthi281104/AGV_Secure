import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, flash
from functools import wraps
from extensions import db 
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

# Remove the top-level import to avoid circular dependency
# Models will be imported locally where needed

# Authentication decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            session['next_url'] = request.url
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


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

# ... (other routes like calculators, profile, etc. remain the same) ...
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

# 3. UPDATE THE CUSTOMERS ROUTE TO FETCH DATA
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