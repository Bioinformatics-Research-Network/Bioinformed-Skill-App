from sqlalchemy import ARRAY, DateTime, JSON, String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Users(Base):
    """
    Shared with Airtable
    """

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, unique=True, index=True)
    github_username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)

    assessments_submitted = relationship(
        "Assessment_Tracker", back_populates="user_info"
    )  # column to check on ongoing assessments


class Reviewers(Base):
    __tablename__ = "reviewers"

    reviewer_id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    assessment_reviewing_id = Column(Integer, ForeignKey("assessment_tracker.entry_id"))

    user_info = relationship("Users", foreign_keys=[user_id])
    assessment_reviewing_info = relationship(
        "Assessment_Tracker", foreign_keys=[assessment_reviewing_id]
    )  # column to check assessment and reviewer relationship


class Assessment_Tracker(Base):
    __tablename__ = "assessment_tracker"

    entry_id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id"))
    status = Column(String)
    last_updated = Column(DateTime)
    latest_commit = Column(String, nullable=False, unique=True)
    reviewer_id = Column(Integer, ForeignKey("reviewers.reviewer_id"))
    log = Column(JSON, nullable=False)

    user_info = relationship(
        "Users", foreign_keys=[user_id], back_populates="assessments_submitted"
    )

    assessment_info = relationship("Assessments", foreign_keys=[assessment_id])
    reviewer_info = relationship("Reviewers", foreign_keys=[reviewer_id])


class Assessments(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True, unique=True, index=True)
    name = Column(String)
    version_number = Column(String)
    change_log = Column(JSON)
    description = Column(String)
    pre_requisites_ids = Column(
        JSON, ForeignKey("assessments.assessment_id")
    )  # divided pre_requisites into '_id' and '_name'
    goals = Column(String)

    pre_requisites_info = relationship("Assessments", remote_side=[assessment_id])
