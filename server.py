import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, flash
from functools import wraps

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# Auth0 Configuration
# 👆 We're continuing from the steps above. Append this to your server.py file.

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
            # Store the original URL user was trying to access
            session['next_url'] = request.url
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# PUBLIC ROUTES (No authentication required)
@app.route('/')
def index():
    """Public homepage - accessible without login"""
    return render_template('index.html')

@app.route("/login")
def login():
    """Auth0 login route"""
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    """Auth0 callback route"""
    token = oauth.auth0.authorize_access_token()
    session["profile"] = token
    
    # Redirect to originally requested URL or dashboard
    next_url = session.pop('next_url', None)
    if next_url:
        return redirect(next_url)
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    """Logout and clear session"""
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

##PROTECTED ROUTES (Authentication required)
@app.route("/dashboard")
@requires_auth
def dashboard():
    """Employee dashboard - requires login"""
    return render_template(
        "dashboard.html",
        session=session.get('profile'),
        userinfo=session['profile']
    )



@app.route('/calculators/emi')
@requires_auth
def emi():
    """EMI Calculator - requires login"""
    return render_template('emi_calculator.html')

@app.route('/calculators/gold')
@requires_auth
def gold():
    """Gold Calculator - requires login"""
    return render_template('gold_calculator.html')

@app.route('/calculators/gold_conversion')
@requires_auth
def gold_cov():
    """Gold Conversion - requires login"""
    return render_template('gold_conversion.html')

@app.route("/profile")
@requires_auth
def profile():
    """User profile page - requires login"""
    return render_template(
        "profile.html",
        userinfo=session['profile']
    )

@app.route("/loans")
@requires_auth
def loans():
    """Loans management - requires login"""
    return render_template("loans.html")

@app.route("/customers")
@requires_auth
def customers():
    """Customer management - requires login"""
    return render_template("customers.html")

@app.route("/reports")
@requires_auth
def reports():
    """Reports and analytics - requires login"""
    return render_template("reports.html")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)  # Use localhost instead of 127.0.0.1