# app/models.py
from sqlalchemy import (
    DateTime,
    JSON,
    String,
    Integer,
    Boolean,
    Column,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Base class for the tables generated in the database"""

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generates the name for the tables
        """
        return cls.__name__.lower()


class Users(UserMixin, Base):
    """
    SQLAlchemy model for the "users" table
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    # From OAuth
    username = Column(String(250), unique=True)
    name = Column(String(250))
    avatar_url = Column(String(250))
    bio = Column(String(250))
    html_url = Column(String(250))
    joined = Column(DateTime)

    # From user input
    first_name = Column(String(250))
    last_name = Column(String(250))
    email = Column(String(250))
    share_with_recruiters = Column(Boolean)
    profile_picture = Column(String(250))
    linkedin_url = Column(String(250))
    cv_url = Column(String(250))
    personal_site = Column(String(250))
    twitter_handle = Column(String(250))
    orcid_id = Column(String(250))
    country = Column(String(250))
    city = Column(String(250))
    current_position = Column(String(250))
    current_institution = Column(String(250))

    # From other sources
    admin = Column(Boolean)
    active = Column(Boolean)
    last_activity = Column(DateTime)
    email_verified = Column(Boolean)
    email_verification_code = Column(String(250))
    email_verification_code_expiry = Column(DateTime)
    onboarded = Column(Boolean)
    reviewer = Column(Boolean)

    def __repr__(self):  # pragma: no cover
        return f"<Users: {self.username}>"


class OAuth(OAuthConsumerMixin, Base):
    __tablename__ = "oauth"
    user_id = Column(Integer, ForeignKey(Users.id))
    user = relationship(Users)


class Reviewers(Base):
    """
    SQLAlchemy model for the "reviewers" table
    """

    __tablename__ = "reviewers"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", name="fk_reviewers_users"))
    assessment_reviewing_id = Column(
        Integer,
        ForeignKey("assessments.id", use_alter=True, name="fk_reviewers_assessments"),
    )


# Create a mapping between the Assessment and Reviewer tables
assessments_to_reviewers = Table(
    "assessments_to_reviewers",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("assessment_id", Integer, ForeignKey("assessments.id")),
    Column("reviewer_id", Integer, ForeignKey("reviewers.id")),
)


class Assessments(Base):
    """
    SQLAlchemy model for the "assessments" table
    """

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    orig_id = Column(Integer)
    name = Column(String(250))
    description = Column(String(250))
    core_skill_areas = Column(String(250))
    languages = Column(String(250))
    types = Column(String(250))
    release_url = Column(String(250))
    prerequisites = Column(String(250))
    classroom_url = Column(String(250))


class AssessmentTracker(Base):
    """
    SQLAlchemy model for the "assessment_tracker" table
    """

    __tablename__ = "assessment_tracker"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", use_alter=True, name="fk_assessment_tracker_users"),
    )
    assessment_id = Column(
        Integer,
        ForeignKey(
            "assessments.id", use_alter=True, name="fk_assessment_tracker_assessments"
        ),
    )
    status = Column(String(250))
    last_updated = Column(DateTime)
    latest_commit = Column(String(250), nullable=False, unique=True)
    reviewer_id = Column(
        Integer,
        ForeignKey(
            "reviewers.id", use_alter=True, name="fk_assessment_tracker_reviewers"
        ),
    )
    log = Column(JSON, nullable=False)


class Badges(Base):
    """
    SQLAlchemy model for the "badges" table
    """

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    name = Column(String(250), unique=True, nullable=False)
    display_on_public = Column(Boolean, nullable=False)
    description = Column(String(250), nullable=False)
    image_url = Column(String(250), unique=True, nullable=False)
    criteria = Column(String(250), nullable=False)
    expiration_date = Column(DateTime)
    tags = Column(String(250))
    standards_alignments = Column(String(250))


class Assertions(Base):
    """
    SQLAlchemy model for the "assertions" table
    """

    __tablename__ = "assertions"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    assessment_tracker_id = Column(
        Integer,
        ForeignKey(
            "assessment_tracker.id",
            use_alter=True,
            name="fk_assertions_assessment_tracker",
        ),
    )
    badge_id = Column(
        Integer, ForeignKey("badges.id", use_alter=True, name="fk_assertions_badges")
    )
    type = Column(String(250))
    credential_id = Column(String(1000), nullable=False, unique=True)
    credential_url = Column(String(1000), nullable=False, unique=True)
    expiration_date = Column(DateTime)
    issue_date = Column(DateTime)
    evidence = Column(Text(10000))
    narrative = Column(Text(10000))
    embed = Column(String(1000))
    created = Column(DateTime)

    # Share info
    share_url = Column(Text(1000))
    linkedin_add_profile_url = Column(Text(2000))
    twitter_share_url = Column(Text(2000))
    facebook_share_url = Column(Text(2000))
    linkedin_share_url = Column(Text(2000))
    embed_card_html = Column(Text(10000))
    embed_badge_html = Column(Text(10000))


class BadgrAuth(Base):
    """
    SQLAlchemy model for the "badgr_auth" table
    """

    __tablename__ = "badgr_auth"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    bearer_token = Column(String(250))
    expires_at = Column(DateTime)
