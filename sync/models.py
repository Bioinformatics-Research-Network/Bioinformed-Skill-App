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


class Badges(Base):
    """
    SQLAlchemy model for the "badges" table
    This comes directly from an API call to badgr.io
    Using config.BADGR_BASE_URL + "/v2/issuers/" + config.BADGR_ISSUER_ID + "/badgeclasses"
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
    badgeclass = Column(
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
