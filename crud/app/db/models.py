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
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict


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


class Users(Base):
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


class OAuth(Base):
    __tablename__ = "oauth"
    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    token = Column(MutableDict.as_mutable(JSON), nullable=False)
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
        ForeignKey(
            "assessments.id", use_alter=True, name="fk_reviewers_assessments"
        ),
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
    name = Column(String(250), unique=True)
    description = Column(String(250))
    core_skill_areas = Column(String(250))
    languages = Column(String(250))
    types = Column(String(250))
    template_repo = Column(String(250))
    latest_release = Column(String(250))
    prerequisites = Column(String(250))
    long_description = Column(Text)
    review_required = Column(Boolean)
    github_org = Column(String(250))
    repo_prefix = Column(String(250))
    install_id = Column(String(250))


class AssessmentTracker(Base):
    """
    SQLAlchemy model for the "assessment_tracker" table
    """

    __tablename__ = "assessment_tracker"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey(
            "users.id", use_alter=True, name="fk_assessment_tracker_users"
        ),
    )
    assessment_id = Column(
        Integer,
        ForeignKey(
            "assessments.id",
            use_alter=True,
            name="fk_assessment_tracker_assessments",
        ),
    )
    status = Column(String(250))
    last_updated = Column(DateTime)
    latest_commit = Column(String(250), nullable=False, unique=True)
    reviewer_id = Column(
        Integer,
        ForeignKey(
            "reviewers.id",
            use_alter=True,
            name="fk_assessment_tracker_reviewers",
        ),
    )
    repo_owner = Column(String(250))
    repo_name = Column(String(250))
    pr_number = Column(Integer)
    log = Column(JSON, nullable=False)


class Badges(Base):
    """
    SQLAlchemy model for the "badges" table

    This comes directly from an API call to badgr.io
    Using config.BADGR_BASE_URL + "/v2/issuers/" +
    config.BADGR_ISSUER_ID + "/badgeclasses"
    """

    __tablename__ = "badges"

    entityId = Column(String(250), primary_key=True, unique=True, index=True)
    entityType = Column(String(250))
    openBadgeId = Column(String(250))
    createdAt = Column(DateTime)
    createdBy = Column(String(250))
    issuer = Column(String(250))
    issuerOpenBadgeId = Column(String(250))
    name = Column(String(250), unique=True)
    image = Column(String(250))
    description = Column(Text)
    achievementType = Column(String(250))
    criteriaUrl = Column(String(250))
    criteriaNarrative = Column(Text)
    alignments = Column(String(250))
    tags = Column(String(250))
    expires = Column(Text)
    extensions = Column(Text)


class Assertions(Base):
    """
    SQLAlchemy model for the "assertions" table
    """

    __tablename__ = "assertions"

    entityId = Column(String(250), unique=True, primary_key=True, index=True)
    entityType = Column(String(250))
    openBadgeId = Column(String(250))
    createdAt = Column(DateTime)
    createdBy = Column(String(250))
    badgeClass = Column(
        String(250),
        ForeignKey(
            "badges.entityId", use_alter=True, name="fk_assertions_badges"
        ),
    )
    recipient_identity = Column(String(500))
    recipient_hashed = Column(Boolean)
    recipient_type = Column(String(250))
    recipient_plaintextIdentity = Column(String(250))
    recipient_salt = Column(String(250))
    issuedOn = Column(DateTime)
    narrative = Column(Text)
    evidence_url = Column(String(250))
    evidence_narrative = Column(Text)
    revoked = Column(Boolean)
    revocationReason = Column(String(250))
    acceptance = Column(String(250))
    expires = Column(DateTime)

    # Share info
    share_url = Column(Text(1000))
    linkedin_add_profile_url = Column(Text(2000))
    twitter_share_url = Column(Text(2000))
    facebook_share_url = Column(Text(2000))
    linkedin_share_url = Column(Text(2000))
    embed_card_html = Column(Text(10000))
    embed_badge_html = Column(Text(10000))

    # Assessment tracker info
    assessment_tracker_id = Column(
        Integer,
        ForeignKey(
            "assessment_tracker.id",
            use_alter=True,
            name="fk_assertions_assessment_tracker",
        ),
    )


class BadgrAuth(Base):
    """
    SQLAlchemy model for the "badgr_auth" table
    """

    __tablename__ = "badgr_auth"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    bearer_token = Column(String(250))
    expires_at = Column(DateTime)
