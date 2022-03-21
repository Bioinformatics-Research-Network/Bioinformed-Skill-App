# to create random data and test other crud utils
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import *
from tests.utils import utils
import random
import string


def create_random_user(
    random_users: int, db: Session # number of random users to create
):  # commit random users in DB

    for i in range(random_users):
        first, last = utils.random_name()
        username = utils.random_username(first, last)
        email = utils.random_email(username)

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


def create_random_reviewers(random_reviewers: int, 
 db: Session
  ):
    user_id_list = utils.random_user_id(random_reviewers)

    for i in range(random_reviewers):
        userid = user_id_list[i]
        db_obj = Reviewers(user_id=userid)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    assert db_obj.user_id == userid


def create_assessments(random_assessments: int, 
 db: Session
 ):
    for i in range(random_assessments):
        name = utils.assessments_name[i]
        desc = utils.assessment_desc[i]
        pre_req = utils.pre_requisite_id[i]

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

def create_random_assessment_tracker(random_assessment_tracker: int, 
db: Session
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
