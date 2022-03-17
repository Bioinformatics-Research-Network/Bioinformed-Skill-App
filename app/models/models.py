from sqlalchemy import ARRAY, DateTime, JSON, String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


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
    assessments_submitted_id = Column(ARRAY[Integer], ForeignKey("assessment_tracker.entry_id"))

    assessments_submitted = relationship(
        "Assessment_Tracker"
    )  # column to check on ongoing assessments




class Reviewers(Base):
    __tablename__ = "reviewers"

    reviewer_id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    assessments_reviewing_id = Column(int, ForeignKey("assessment_tracker.entry_id"))

    user_info = relationship("User")
    assessments_reviewing_info = relationship(
        "Assessment_Tracker"
    )  # column to check assessment and reviewer relationship


class Assessment_Tracker(Base):
    __tablename__ = "assessment_tracker"

    entry_id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    status = Column(String)
    last_updated = Column(DateTime)
    latest_commit = Column(String, nullable=False, unique=True)
    reviewer_ids = Column(Integer, ForeignKey("reviewers.id"))
    log = Column(JSON, nullable=False)

    user_info = relationship("User")
    assessment_info = relationship("Assessments")
    reviewers_info = relationship("Reviewers")
    

class Assessments(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True, unique=True, index=True)
    name = Column(String)
    version_number = Column(String)
    change_log = Column(JSON)
    description = Column(String)
    pre_requisites_id = Column(
        Integer, ForeignKey("assessments.id")
    )  # divided pre_requisites into '_id' and '_name'
    goals = Column(String)
    
    pre_requisites_info = relationship("Assessments", remote_side=[name])
    
