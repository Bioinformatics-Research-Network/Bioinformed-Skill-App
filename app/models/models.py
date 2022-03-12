from sqlalchemy import ARRAY, DateTime, JSON, String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base


class Users(Base):
    """
    Shared with Airtable
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    github_username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    assessments_id = Column(Integer, ForeignKey("assessment_tracker.entry_id"))
    assessments = relationship(
        "Assessment_Tracker", back_populates="user"
    )  # column to check on ongoing assessments




class Reviewers(Base):
    __tablename__ = "reviewers"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    assessments_reviewing = relationship(
        "Assessment_Tracker", back_populates="reviewers"
    )  # column to check assessment and reviewer relationship


class Assessment_Tracker(Base):
    __tablename__ = "assessment_tracker"
    entry_id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="ongoing_assessments")
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    status = Column(String)
    last_updated = Column(DateTime)
    latest_commit = Column(String, nullable=False, unique=True)
    reviewer_id = Column(Integer, ForeignKey("reviewers.id"))
    reviewers = relationship("Reviewers", back_populates="assessments_reviewing")
    log = Column(JSON, nullable=False)


class Assessments(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    name = Column(String)
    version_number = Column(String)
    change_log = Column(JSON)
    description = Column(String)
    pre_requisites_id = Column(
        Integer, ForeignKey("assessments.id")
    )  # divided pre_requisites into '_id' and '_name'
    pre_requisites = relationship("Assessments", remote_side=[name])
    goals = Column(String)
