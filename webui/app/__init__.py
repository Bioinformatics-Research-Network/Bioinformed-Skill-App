from .routes import routes
from .config import settings

import atexit
import os

from flask import Flask

from . import auth, db, utils
from .db import db_session, init_db


# Flask config
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    app.secret_key = (
        settings.FLASK_APP_SECRET_KEY
    )  # Replace this with your own secret!
    app.register_blueprint(auth.oauth.github_blueprint, url_prefix="/login")
    app.config["SQLALCHEMY_DATABASE_URI"] = db.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Blueprints
    app.register_blueprint(routes)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    init_db()
    auth.login_manager.init_app(app)

    # On server end, remove the db session
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    print("App initialized")

    return app
