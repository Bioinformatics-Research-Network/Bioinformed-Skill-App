# This

from datetime import datetime
import random
from app import models
from app.crud import random_data_crud
from app.db.initiate_db import init_db
from app.db.session import SessionLocal
from app.models import *
from sqlalchemy.orm import Session
import string
from datetime import datetime

random.seed(42)

init_db()


def bot_testing_data(db: Session):
    """Used to create predefined data for bot testing"""

    # creating users for bot testing
    db_obj = models.Users(
        email="tests@bioresnet.org",
        github_username="millerh1",
        first_name="BotUser",
        last_name="Tests",
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    db_obj = models.Users(
        email="tests2@bioresnet.org",
        github_username="itchytummy",
        first_name="BotReviewer",
        last_name="Reviews",
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # reviewers for bot testing
    db_obj = models.Reviewers(user_id=1)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    db_obj = models.Reviewers(user_id=2)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # assessment for bot testing
    db_obj = models.Assessments(
        name="Test",
        version_number="1",
        change_log=[{"Version No.": "1", "Updated": str(datetime.utcnow())}],
        description="Test decription",
        pre_requisites_ids=None,
        goals="Test goals",
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # assessment tracker for bot testing
    cmt = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
    db_obj = models.AssessmentTracker(
        assessment_id=1,
        user_id=1,
        latest_commit=cmt,
        last_updated=datetime.utcnow(),
        status="Initiated",
        log=[
            {
                "Status": "Initiated",
                "Updated": str(datetime.utcnow()),
                "Commit": cmt,
            }
        ],
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)


def create_fake_data(user=20, reviewer=20, assessment=10, assessment_tracker=50):

    """
    To create fake data for the database. It adds fake data to the pre-existing database.
    If database doesn't exist already it will create the database "fake_skill_cert.db".
    The name of db can be altered from app/db/session.py .
    To create the database suitable for the SKILL-CERT-API:
    1. Go to the Skill-cert-API/app directory.
        This is necessary to create the db in the required directory for the API to read from.
    2. Run the following command:
        `python ./db/create_fake_data.py` - Linux; change to backslash for Windows

    :param user: inputs number of fake user entries to be created. Default = 100.
    :param reviewer: inputs number of fake reviewer entries to be created. Default = 100.
    :param assessment: inputs number of fake assessment entries to be created. Default = 100.
    :param assessment_tracker: inputs number of fake assessment_tracker entries to be created. Default = 100.
    """
    db = SessionLocal()

    random.seed(42)

    bot_testing_data(db=db)
    random_data_crud.create_random_user(db=db, random_users=user)
    random_data_crud.create_random_reviewers(db=db, random_reviewers=reviewer)
    random_data_crud.create_assessments(db=db, random_assessments=assessment)
    random_data_crud.create_random_assessment_tracker(
        db=db, random_assessment_tracker=assessment_tracker
    )

    db.close()


create_fake_data()
