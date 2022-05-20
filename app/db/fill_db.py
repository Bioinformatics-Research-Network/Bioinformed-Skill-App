# This

from datetime import datetime
from app import models
from app.db.initiate_db import init_db
from app.db.session import SessionLocal
from app.models import *
from sqlalchemy.orm import Session


users = [
    {
        "username": "millerh1",
        "name": "Henry Miller"
    },
    {
        "username": "bioresnet",
        "name": "Henry (bioresnet)",
    },
]
reviewers = [
    {
        "id": 1,
    },
    {
        "id": 2,
    },
]
assessments = [
    {
        "name": "Test",
        "version_number": 1,
        "change_log": [{"version": "1", "last_updated": str(datetime.utcnow())}],
        "description": "Test decription",
        "goals": "Test goals",
    },
]

assessment_tracker = [
    {
        "id": 1,
        "id": 1,
        "status": "completed",
        "last_updated": str(datetime.utcnow()),
        "latest_commit": "commit_hash",
        "id": 2,
        "log": [{"version": "1", "last_updated": str(datetime.utcnow())}],
    },
]


def add_user(user_entry: dict, db: Session):
    """
    To add a user to the database.

    :param user_entry: dictionary of user data.
    :param db: database session.
    """
    print("Adding user: {}".format(user_entry["name"]))
    db_obj = models.Users(
        username=user_entry["username"],
        name=user_entry["name"],
    )
    # Add the entry
    db.commit()
    db.add(db_obj)


def add_reviewer(reviewer_entry: dict, db: Session):
    """
    To add a reviewer to the database.

    :param reviewer_entry: dictionary of reviewer data.
    :param db: database session.
    """
    print("Adding reviewer: {}".format(reviewer_entry["id"]))
    db_obj = models.Reviewers(
        reviewer_id=reviewer_entry["id"],
    )
    # Add the entry
    db.commit()
    db.add(db_obj)


def add_assessment(assessment_entry: dict, db: Session):
    """
    To add an assessment to the database.

    :param assessment_entry: dictionary of assessment data.
    :param db: database session.
    """
    print("Adding assessment: {}".format(assessment_entry["name"]))
    db_obj = models.Assessments(
        name=assessment_entry["name"],
        version_number=assessment_entry["version_number"],
        change_log=assessment_entry["change_log"],
        description=assessment_entry["description"],
        goals=assessment_entry["goals"],
    )
    # Add the entry
    db.commit()
    db.add(db_obj)


def add_assessment_tracker(assessment_tracker_entry: dict, db: Session):
    """
    To add an assessment tracker to the database.

    :param assessment_tracker_entry: dictionary of assessment tracker data.
    :param db: database session.
    """
    print("Adding assessment tracker: {}".format(assessment_tracker_entry["id"]))
    db_obj = models.AssessmentTracker(
        assessment_id=assessment_tracker_entry["id"],
        assessment_id=assessment_tracker_entry["id"],
        status=assessment_tracker_entry["status"],
        last_updated=assessment_tracker_entry["last_updated"],
        latest_commit=assessment_tracker_entry["latest_commit"],
        assessment_id=assessment_tracker_entry["id"],
        log=assessment_tracker_entry["log"],
    )
    # Add the entry
    db.commit()
    db.add(db_obj)


def create_database():
    """
    To create the database.
    """
    db = SessionLocal()


    # # Delete database if it exists
    # db.execute("DROP DATABASE IF EXISTS `skill-db`")


    [add_user(user, db) for user in users]
    [add_reviewer(reviewer, db) for reviewer in reviewers]
    [add_assessment(assessment, db) for assessment in assessments]
    [add_assessment_tracker(assessment_tracker, db) for assessment_tracker in assessment_tracker]
    db.flush()
    db.close()


if __name__ == "__main__":
    init_db()
    create_database()
