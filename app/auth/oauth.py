import os

from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound

from app.models import db, OAuth, Users
from app import config


github_blueprint = make_github_blueprint(
    client_id=config.GH_OAUTH_CLIENT_ID,
    client_secret=config.GH_OAUTH_CLIENT_SECRET,
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
)


@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    info = github.get("/user")
    if info.ok:
        account_info = info.json()
        username = account_info["login"]

        query = Users.query.filter_by(username=username)
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
            db.session.add(user)
            db.session.commit()
        login_user(user)
