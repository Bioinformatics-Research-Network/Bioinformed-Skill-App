# to create random data and test other crud utils
from fastapi import Depends
from datetime import datetime
from sqlalchemy.orm import Session
from app.api.services import get_db
from app.models.models import *
from app.utils import random_data_utils
import random
import string


def create_random_user(
    random_users: int, db: Session  # number of random users to create
):  # commit random users in DB

    for i in range(random_users):
        first, last = random_data_utils.random_name()
        username = random_data_utils.random_username(first, last)
        email = random_data_utils.random_email(username)

        db_obj = Users(
            email=email, github_username=username, first_name=first, last_name=last
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj


def create_random_reviewers(random_reviewers: int,  db: Session):
    user_id_list = random_data_utils.random_user_id(random_reviewers)

    for i in range(random_reviewers):
        userid = user_id_list[i]
        db_obj = Reviewers(user_id=userid)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj


def create_assessments(random_assessments: int, db: Session):
    for i in range(random_assessments):
        name = random_data_utils.assessments_name[i]
        desc = random_data_utils.assessment_desc[i]
        pre_req = random_data_utils.pre_requisite_id[i]

        db_obj = Assessments(
            name=name,
            version_number="1",
            change_log={"Created": str(datetime.now())},
            description=desc,
            pre_requisites_ids=pre_req,
            goals=desc,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj

def create_random_assessment_tracker( random_assessment_tracker: int,  db: Session):
    for i in range(random_assessment_tracker):
        commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))

        db_obj = Assessment_Tracker(
            user_id=random.randint(1, 100),
            assessment_id=random.randint(1, 10),
            status="Created",
            last_updated=datetime.now(),
            latest_commit=commit,
            log={"Created": str(datetime.now())},
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj
