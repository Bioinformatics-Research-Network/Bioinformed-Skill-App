from sqlalchemy import (
    DateTime,
    JSON,
    String,
    Integer,
    Column,
)
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


class AssessmentTracker(Base):
    """
    SQLAlchemy model for the "assessment_tracker" table
    """

    __tablename__ = "assessment_tracker"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(
        Integer,
    )
    assessment_id = Column(
        Integer,
    )
    status = Column(String(250))
    last_updated = Column(DateTime)
    latest_commit = Column(String(250), nullable=False, unique=True)
    reviewer_id = Column(
        Integer,
    )
    repo_owner = Column(String(250))
    repo_name = Column(String(250))
    pr_number = Column(Integer)
    log = Column(JSON, nullable=False)
