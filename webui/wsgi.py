import os
from app import create_app
from werkzeug.middleware.proxy_fix import ProxyFix

app = create_app()

# For production, we want to use the proxy fix middleware
# The docker container will forward the requests to the backend
# Required for OAuth2 authentication to work
# Found from reading the Flask-Dance docs
if os.environ.get("APP_ENV") == "production":
    app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == "__main__":
    app.run()
