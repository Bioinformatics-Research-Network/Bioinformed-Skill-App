import os

# Retrieve the github client id from the environment
GH_OAUTH_CLIENT_ID = os.environ.get("GH_OAUTH_CLIENT_ID")

# Retrieve the github client secret from the environment
GH_OAUTH_CLIENT_SECRET = os.environ.get("GH_OAUTH_CLIENT_SECRET")

# Set app secret key
FLASK_APP_SECRET_KEY = os.environ.get("FLASK_APP_SECRET_KEY")

# Connection details for RDS
RDS_ENDPOINT = os.environ.get("RDS_ENDPOINT")
RDS_PORT = os.environ.get("RDS_PORT")
RDS_DB_NAME = os.environ.get("RDS_DB_NAME")
RDS_USERNAME = os.environ.get("RDS_USERNAME")
RDS_PASSWORD = os.environ.get("RDS_PASSWORD")

# Privacy Policy URL
PRIVACY_POLICY_URL = (
    "https://www.privacypolicies.com/live/bb7b8b6b-32e1-45c1-be17-814529aeb5cb"
)

# Secrets
SECRET_KEY = os.environ.get("FLASK_SECURITY_KEY")
SECURITY_PASSWORD_SALT = os.environ.get("FLASK_SECURITY_PASSWORD_SALT")

# Mandrill API key
MANDRILL_API_KEY = os.environ.get("MANDRILL_API_KEY")

# Email verification expiration
EMAIL_VERIFICATION_EXPIRATION = 3600

# Site URL
SITE_URL = "http://localhost:5000"
