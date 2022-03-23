# to create random data and test other crud utils
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.models.models import *
from app.utils import random_data_utils
from app.crud.random_data_crud import *
import random
import string


def test_create_random_user(
    db: Session 
): 
    db_obj = create_random_user(db=db, random_users=1)

    assert db_obj.first_name in random_data_utils.first_list
    assert db_obj.last_name in random_data_utils.last_list
    assert type(db_obj.github_username) == str
    assert type(db_obj.email) == str


def test_create_random_reviewers(db: Session):
    
    db_obj = create_random_reviewers(db=db, random_reviewers=1)

    assert type(db_obj.user_id) == int


def test_create_assessments(
    db: Session
):
    db_obj = create_assessments(db=db, random_assessments=1)

    assert db_obj.name in random_data_utils.assessments_name
    assert db_obj.description in random_data_utils.assessment_desc
    assert db_obj.goals in random_data_utils.assessment_desc
    assert db_obj.pre_requisites_ids in random_data_utils.pre_requisite_id
    assert db_obj.version_number == "1"


def test_create_random_assessment_tracker(
    db: Session
):
    db_obj=create_random_assessment_tracker(db=db, random_assessment_tracker=1)

    assert db_obj.status == "Created"
    assert type(db_obj.latest_commit) == str
    assert type(db_obj.assessment_id) == int
    assert type(db_obj.user_id) == int
