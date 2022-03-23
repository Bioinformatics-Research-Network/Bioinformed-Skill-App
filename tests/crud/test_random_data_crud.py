# to create random data and test other crud utils
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import *
from app.utils import random_data_utils
import random
import string


def test_create_random_user(
    db: Session, random_users: int = 100  # number of random users to create
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

    assert db_obj.first_name == first
    assert db_obj.last_name == last
    assert db_obj.github_username == username
    assert db_obj.email == email


def test_create_random_reviewers(db: Session, random_reviewers: int = 20):
    user_id_list = random_data_utils.random_user_id(random_reviewers)

    for i in range(random_reviewers):
        userid = user_id_list[i]
        db_obj = Reviewers(user_id=userid)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    assert db_obj.user_id == userid


def test_create_assessments(
    db: Session,
    random_assessments: int = 10,
):
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

    assert db_obj.name == name
    assert db_obj.description == desc
    assert db_obj.goals == desc
    assert db_obj.pre_requisites_ids == pre_req
    assert db_obj.version_number == "1"


def test_create_random_assessment_tracker(
    db: Session, random_assessment_tracker: int = 10
):
    for i in range(random_assessment_tracker):
        commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        userid = random.randint(1, 100)
        assessmentid = random.randint(1, 10)
        db_obj = Assessment_Tracker(
            user_id=userid,
            assessment_id=assessmentid,
            status="Created",
            last_updated=datetime.now(),
            latest_commit=commit,
            log={"Created": str(datetime.now())},
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    assert db_obj.status == "Created"
    assert db_obj.latest_commit == commit
    assert db_obj.assessment_id == assessmentid
    assert db_obj.user_id == userid
