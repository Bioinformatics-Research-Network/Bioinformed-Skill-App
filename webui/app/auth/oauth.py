import os

from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound

from app.models import OAuth, Users
from app.db import db_session
from app.config import settings

# Set the oauth insecure=True to allow for local testing
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Create the github blueprint and register it
github_blueprint = make_github_blueprint(
    client_id=settings.GH_OAUTH_CLIENT_ID,
    client_secret=settings.GH_OAUTH_CLIENT_SECRET,
    storage=SQLAlchemyStorage(
        OAuth,
        db_session,
        user=current_user,
        user_required=False,
    ),
)


# Add the github blueprint to the app
@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    info = github.get("/user")
    if info.ok:
        account_info = info.json()
        username = account_info["login"]

        # Query Users table to see if user exists
        query = db_session.query(Users).filter_by(username=username)

        try:
            user = query.one()
        except NoResultFound:
            user = Users(
                username=username,
                name=account_info["name"],
                avatar_url=account_info["avatar_url"],
                bio=account_info["bio"],
                email=account_info["email"],
                html_url=account_info["html_url"],
                email_verified=False,
                onboarded=False,
            )

            db_session.add(user)
            db_session.commit()
        login_user(user)
