# This
from app.crud import random_data_crud
from app.db.initiate_db import init_db
from app.db.session import SessionLocal

init_db()


def create_fake_data(user=100, reviewer=20, assessment=10, assessment_tracker=20):
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

    random_data_crud.create_random_user(db=db, random_users=user)
    random_data_crud.create_random_reviewers(db=db, random_reviewers=reviewer)
    random_data_crud.create_assessments(db=db, random_assessments=assessment)
    random_data_crud.create_random_assessment_tracker(
        db=db, random_assessment_tracker=assessment_tracker
    )

    db.close()


create_fake_data()
