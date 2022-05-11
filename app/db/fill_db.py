# This

from datetime import datetime
from app import models
from app.db.initiate_db import init_db_real
from app.db.session import SessionLocalReal
from app.models import *
from sqlalchemy.orm import Session


init_db_real()


users = [
    {
        "email": "test@bioresnet.org",
        "github_username": "millerh1",
        "first_name": "Henry",
        "last_name": "Miller",
    },
    {
        "email": "test2@bioresnet.org",
        "github_username": "itchytummy",
        "first_name": "Anmol",
        "last_name": "Singh",
    },
]
reviewers = [
    {
        "user_id": 1,
        "assessment_reviewing_id": 1,
    },
    {
        "user_id": 2,
        "assessment_reviewing_id": 1,
    },
]
assessments = [
    {
        "name": "Test Assessment",
        "version_number": 1,
        "change_log": [{"version": "1", "last_updated": str(datetime.utcnow())}],
        "description": "Test decription",
        "pre_requisites_ids": None,
        "goals": "Test goals",
    },
]


def add_user(user_entry: dict, db: Session):
    """
    To add a user to the database.

    :param user_entry: dictionary of user data.
    :param db: database session.
    """
    print("Adding user: {}".format(user_entry["email"]))
    db_obj = models.Users(
        email=user_entry["email"],
        github_username=user_entry["github_username"],
        first_name=user_entry["first_name"],
        last_name=user_entry["last_name"],
    )
    # Add the entry
    db.add(db_obj)
    db.commit()


def add_reviewer(reviewer_entry: dict, db: Session):
    """
    To add a reviewer to the database.

    :param reviewer_entry: dictionary of reviewer data.
    :param db: database session.
    """
    print("Adding reviewer: {}".format(reviewer_entry["user_id"]))
    db_obj = models.Reviewers(
        user_id=reviewer_entry["user_id"],
        assessment_reviewing_id=reviewer_entry["assessment_reviewing_id"],
    )
    # Add the entry
    db.add(db_obj)
    db.commit()


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
        pre_requisites_ids=assessment_entry["pre_requisites_ids"],
        goals=assessment_entry["goals"],
    )
    # Add the entry
    db.add(db_obj)
    db.commit()


def create_database():

    db = SessionLocalReal()
    [add_user(user, db) for user in users]
    [add_reviewer(reviewer, db) for reviewer in reviewers]
    [add_assessment(assessment, db) for assessment in assessments]
    db.flush()
    db.close()


create_database()
