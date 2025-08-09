import secrets
import uuid

print("=== AGV Finance App Secrets Generator ===")
print()

# Generate APP_SECRET_KEY
secret_key = secrets.token_hex(32)
print(f"APP_SECRET_KEY={secret_key}")
print()

print("Add this to your .env file:")
print(f"""
# Auth0 Configuration (Get these from Auth0 Dashboard)
AUTH0_CLIENT_ID=your_auth0_client_id_here
AUTH0_CLIENT_SECRET=your_auth0_client_secret_here  
AUTH0_DOMAIN=your_auth0_domain_here

# App Secret Key (Generated)
APP_SECRET_KEY={secret_key}
""")

print("Next steps:")
print("1. Create Auth0 application at https://auth0.com/")
print("2. Get your Client ID, Client Secret, and Domain")
print("3. Replace the placeholders in .env file")
print("4. Set Callback URL in Auth0: http://localhost:5000/callback")
print("5. Set Logout URL in Auth0: http://localhost:5000/")