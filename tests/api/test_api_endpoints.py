# starting with tests for api endpoints
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import Json
from sqlalchemy.orm import Session
from app import models
from app.crud.crud import verify_member
from app.schemas import schemas

# /api/init-assessment
def test_init_assessment(
    client: TestClient,
    db: Session
    ):
    user = db.query(models.Users).first()
    request_json = {
        "user": {
            "github_username": user.github_username
            },
        "assessment_tracker": {
            "assessment_name": "Back-End Web Development",
            "latest_commit": "testcommit8451adafadace45a41c65ea"
            }
    }
    response = client.post("/api/init_assessment", json = request_json)

    assert response.status_code == 200
    data = response.json()
    assert data["Initiated"] == True
    assert type(data["User_first_name"]) == str

    
# /api/init-check
def test_init_check(
    client: TestClient,
    db: Session
    ):
    github_username = db.query(models.Users)\
        .filter(models.Users.user_id == 1)\
        .with_entities(models.Users.github_username).scalar()
    request_json = {
        "github_username": github_username,
        "assessment_name": "Back-End Web Development",
        "commit": "testcommit12345qwerty"
    }

    response = client.post("/init_check", json=request_json)
    
    assert response.status_code == 200
    assert response.json() == {"Logs updated": "init-check"}

# /api/update
def test_update(
    client: TestClient,
    db: Session
    ):
    github_username = db.query(models.Users)\
        .filter(models.Users.user_id == 1)\
        .with_entities(models.Users.github_username).scalar()
    request_json = {
        "github_username": github_username,
        "assessment_name": "Back-End Web Development",
        "commit": "testcommit12345qwerty"
    }
    logs = {"Updated": str(datetime.utcnow()),
            "Commit": "testupdatecommit123"}

    response = client.patch("/update", json=request_json, params=logs)
    
    assert response.status_code == 200
    assert response.json() == {"Logs Updated": "update"}

# /api/approve-assessment
def test_approve_assessment(
    client: TestClient,
    db: Session
    ):
    github_username = db.query(models.Users)\
        .filter(models.Users.user_id == 1)\
        .with_entities(models.Users.github_username).scalar() # the reviewer and member username is assumed to be same for test purposes
    request_json = {
        "reviewer_username": github_username,
        "member_username": github_username,
        "assessment_name": "Back-End Web Development"
    }
    response = client.patch("/approve_assessment", json=request_json)
    
    assert response.status_code == 200
    assert response.json() == {"Assessment Approved": True}
# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer