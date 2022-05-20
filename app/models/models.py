# app/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin


db = SQLAlchemy()


class Users(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # From OAuth
    username = db.Column(db.String(250), unique=True)
    name = db.Column(db.String(250))
    avatar_url = db.Column(db.String(250))
    bio = db.Column(db.String(250))
    html_url = db.Column(db.String(250))
    joined = db.Column(db.DateTime)

    # From user input
    first_name = db.Column(db.String(250))
    last_name = db.Column(db.String(250))
    email = db.Column(db.String(250))
    share_with_recruiters = db.Column(db.Boolean)
    profile_picture = db.Column(db.String(250))
    linkedin_url = db.Column(db.String(250))
    cv_url = db.Column(db.String(250))
    twitter_url = db.Column(db.String(250))
    orcid_id = db.Column(db.String(250))
    country = db.Column(db.String(250))
    city = db.Column(db.String(250))
    current_position = db.Column(db.String(250))
    current_institution = db.Column(db.String(250))

    # From other sources
    admin = db.Column(db.Boolean)
    active = db.Column(db.Boolean)
    last_activity = db.Column(db.DateTime)
    email_verified = db.Column(db.Boolean)
    email_verification_code = db.Column(db.String(250))
    email_verification_code_expiry = db.Column(db.DateTime)
    onboarded = db.Column(db.Boolean)
    reviewer = db.Column(db.Boolean)
    
    def __repr__(self):
        return f"<Users: {self.username}>"
    

class Reviewers(db.Model):
    """
    SQLAlchemy model for the "reviewers" table
    """

    __tablename__ = "reviewers"

    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", name="fk_reviewers_users"))
    assessment_reviewing_id = db.Column(
        db.Integer, db.ForeignKey("assessment_tracker.id", use_alter=True, name="fk_reviewers_assessment_tracker")
    )
    

class OAuth(OAuthConsumerMixin, db.Model):
    __tablename__ = "oauth"
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    user = db.relationship(Users)


class Assessments(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    orig_id = db.Column(db.Integer)
    name = db.Column(db.String(250))
    description = db.Column(db.String(250))
    core_skill_areas = db.Column(db.String(250))
    languages = db.Column(db.String(250))
    types = db.Column(db.String(250))
    release_url = db.Column(db.String(250))
    prerequisites = db.Column(db.String(250))
    classroom_url = db.Column(db.String(250))


class AssessmentTracker(db.Model):
    """
    SQLAlchemy model for the "assessment_tracker" table
    """

    __tablename__ = "assessment_tracker"

    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", use_alter=True, name="fk_assessment_tracker_users"))
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("assessments.id", use_alter=True, name="fk_assessment_tracker_assessments")
    )
    status = db.Column(db.String(250))
    last_updated = db.Column(db.DateTime)
    latest_commit = db.Column(db.String(250), nullable=False, unique=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("reviewers.id", use_alter=True, name="fk_assessment_tracker_reviewers"))
    log = db.Column(db.JSON, nullable=False)


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
