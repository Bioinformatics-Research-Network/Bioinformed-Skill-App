from sqlalchemy import DateTime, JSON, String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    github_username = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class Reviewers(Base):
    __tablename__ = "reviewers"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    user = relationship("User")

class Assessment_Tracker(Base):
    __tablename__ = "assessment_tracker"
    entry_id = Column(Integer, primary_key=True, unique=True, index=True)
    user = relationship("User")
    assessment_id= Column(Integer, ForeignKey("assessments.id"))
    status = Column(String)
    last_updated = Column(DateTime)
    latest_commit = Column(String, nullable=False, unique=True)
    reviewer = relationship("Reviewers")
    # Log    # Working on it
    #     JSON containing full log of review process, including timestamps

class Assessments(Base): # working on it
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, unique=True, index=True)
