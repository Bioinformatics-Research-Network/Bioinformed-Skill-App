# to create random data and test other crud utils
from sqlalchemy.orm import Session
from app.utils import random_data_utils
from app.crud import random_data_crud


def test_create_random_user(db: Session):
    db_obj = random_data_crud.create_random_user(db=db, random_users=1)
    assert type(db_obj.username) == str
    assert type(db_obj.name) == str


def test_create_random_reviewers(db: Session):

    db_obj = random_data_crud.create_random_reviewers(db=db, random_reviewers=1)

    assert type(db_obj.id) == int


def test_create_random_assessment_tracker(db: Session):
    db_obj = random_data_crud.create_random_assessment_tracker(
        db=db, random_assessment_tracker=1
    )

    assert db_obj.status == "Initiated"
    assert type(db_obj.latest_commit) == str
    assert type(db_obj.id) == int
    assert type(db_obj.id) == int
