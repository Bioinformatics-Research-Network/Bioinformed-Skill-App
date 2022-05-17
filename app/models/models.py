# app/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True)
    name = db.Column(db.String())
    avatar_url = db.Column(db.String())
    bio = db.Column(db.String())
    email = db.Column(db.String())
    html_url = db.Column(db.String())
    

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


class Assessments(db.Model):
    __tablename__ = "assessments"

    assessment_id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    orig_id = db.Column(db.Integer)
    name = db.Column(db.String)
    description = db.Column(db.String)
    core_skill_areas = db.Column(db.String)
    languages = db.Column(db.String)
    types = db.Column(db.String)
    release_url = db.Column(db.String)
    prerequisites = db.Column(db.String)
    classroom_url = db.Column(db.String)
    


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
