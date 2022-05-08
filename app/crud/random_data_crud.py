# to create random data and test other crud utils
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import models
from app.utils import random_data_utils
import random
import string

random.seed(42)


def create_random_user(random_users: int, db: Session):
    """
    Creates random fake entries for User table

    :param db: Generator for Session of database
    :param random_user: number of fake user entries to be generated

    :returns: User object for the last fake entry generated
    """

    for i in range(random_users):
        first, last = random_data_utils.random_name()
        username = random_data_utils.random_username(first, last)
        email = random_data_utils.random_email(username)

        db_obj = models.Users(
            email=email,
            github_username=username,
            first_name=first,
            last_name=last,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj


def create_random_reviewers(random_reviewers: int, db: Session):
    """
    Creates random fake entries for reviewer table

    :param db: Generator for Session of database
    :param random_reviewer: number of fake reviewer entries to be generated

    :returns: Reviewer object for the last fake entry generated
    """
    user_id_count = db.query(models.Users).count()

    for i in range(random_reviewers):
        userid = random.randint(1, user_id_count)
        db_obj = models.Reviewers(user_id=userid)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj


def create_assessments(random_assessments: int, db: Session):
    """
    Creates random fake entries for assessment table

    :param db: Generator for Session of database
    :param random_assessments: number of fake assessments entries to be generated

    :returns: Assessment object for the last fake entry generated
    """
    for i in range(random_assessments):
        name = random_data_utils.assessments_name[i]
        desc = random_data_utils.assessment_desc[i]
        pre_req = random_data_utils.pre_requisite_id[i]

        db_obj = models.Assessments(
            name=name,
            version_number="1",
            change_log=[{"Version No.": "1", "Updated": str(datetime.utcnow())}],
            description=desc,
            pre_requisites_ids=pre_req,
            goals=desc,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj


def create_random_assessment_tracker(random_assessment_tracker: int, db: Session):
    """
    Creates random fake entries for assessment_tracker table

    :param db: Generator for Session of database
    :param random_assessment_tracker: number of fake assessment_tracker entries to be generated

    :returns: Assessment_tracker object for the last fake entry generated
    """
    user_id_count = db.query(models.Users).count()
    assessment_id_count = db.query(models.Assessments).count()
    for i in range(random_assessment_tracker):
        commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        userid = random.randint(1, user_id_count)
        assessmentid = random.randint(2, assessment_id_count)
        db_obj = models.AssessmentTracker(
            user_id=userid,
            assessment_id=assessmentid,
            status="Initiated",
            last_updated=datetime.utcnow(),
            latest_commit=commit,
            log=[
                {
                    "Status": "Initiated",
                    "Updated": str(datetime.utcnow()),
                    "Commit": commit,
                }
            ],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj
