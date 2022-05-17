import os

# Retrieve the github client id from the environment
GH_OAUTH_CLIENT_ID = os.environ.get("GH_OAUTH_CLIENT_ID")

# Retrieve the github client secret from the environment
GH_OAUTH_CLIENT_SECRET = os.environ.get("GH_OAUTH_CLIENT_SECRET")

# Set app secret key
FLASK_APP_SECRET_KEY = os.environ.get("FLASK_APP_SECRET_KEY")

# Database URI
SQLALCHEMY_DATABASE_URI = "sqlite:///./app_data.db"
