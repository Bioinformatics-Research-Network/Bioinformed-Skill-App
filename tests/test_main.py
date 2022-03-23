from fastapi.testclient import TestClient
from fastapi import Depends
from app.crud.random_data_crud import *
from tests.utils.test_db import *
from sqlalchemy.orm import Session
from app.api import services

init()

def test_random_data(
    client: TestClient,
    db: Session
) -> None:
    create_random_user(db=db, random_users=1)
    create_random_reviewers(db=db, random_reviewers=1)
    create_assessments(db=db, random_assessments=1)
    create_random_assessment_tracker(db=db, random_assessment_tracker=1)
    r = client.get("/create_random_data")
    assert r.status_code == 200
    assert r.json() == {"Working"}
    