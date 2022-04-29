# starting with tests for api endpoints
from datetime import datetime
from fastapi import HTTPException
import json
import random
import string
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from app import models


# /api/init-assessment
def test_init_assessment(
    client: TestClient,
    db: Session
    ):
    github_username = db.query(models.Users)\
        .filter(models.Users.user_id == 1)\
        .with_entities(models.Users.github_username).scalar()

    assessment_name = db.query(models.Assessments)\
        .filter(models.Assessments.assessment_id == 1)\
        .with_entities(models.Assessments.name).scalar()

    request_json = {
        "user": {
            "github_username": github_username
            },
        "assessment_tracker": {
            "assessment_name": assessment_name,
            "latest_commit": ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 10))
            }
    }
    response = client.post("/api/init_assessment", json = request_json)

    assert response.status_code == 200
    data = response.json()
    assert data["Initiated"] == True
    assert type(data["User_first_name"]) == str

    error_json = {
        "user": {
            "github_username": "errorhandling"
            },
        "assessment_tracker": {
            "assessment_name": "error",
            "latest_commit": 'errors'
            }
    }
    response_error = client.post("/api/init_assessment", json = error_json)

    assert response_error.status_code == 404
    assert response_error.json() == {"detail":"User not found"}


    
# /api/init-check
def test_init_check(
    client: TestClient,
    db: Session
    ):
    github_username = db.query(models.Users)\
        .filter(models.Users.user_id == 1)\
        .with_entities(models.Users.github_username).scalar()
    assessment_name = db.query(models.Assessments)\
        .filter(models.Assessments.assessment_id == 1)\
        .with_entities(models.Assessments.name).scalar()
    
    request_json = {
        "github_username": github_username,
        "assessment_name": assessment_name,
        "commit": ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 10))
    }

    response = client.post("/api/init_check", json=request_json)
    
    assert response.status_code == 200
    assert response.json() == {"Logs updated": "init-check"}
    error_json = {
        "github_username": "error",
        "assessment_name": "error",
        "commit": "error"
    }
    response_error = client.post("/api/init_check", json=error_json)
    assert response_error.status_code == 404
    assert response_error.json() == {"detail": "User Not Registered"}

# /api/update
def test_update(
    client: TestClient,
    db: Session
    ):
    github_username = db.query(models.Users)\
        .filter(models.Users.user_id == 1)\
        .with_entities(models.Users.github_username).scalar() 

    assessment_name = db.query(models.Assessments)\
        .filter(models.Assessments.assessment_id == 1)\
        .with_entities(models.Assessments.name).scalar()

    commit = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 10))
    logs = json.dumps({"Updated": str(datetime.utcnow()), "Commit": commit})
    request_json ={
        "asses_track_info": {
            "github_username": github_username,
            "assessment_name": assessment_name,
            "commit": commit
            },
        "update_logs": {
            "log": logs
            }
        }
    
    response = client.patch("/api/update", json=request_json)
    
    assert response.status_code == 200
    assert response.json() == {"Logs Updated": "update"}

    error_json = {
        "asses_track_info": {
            "github_username": "error",
            "assessment_name": "error",
            "commit": "error"
            },
        "update_logs": {
            "log": json.dumps({"Error":"update log"})
            }
    }
    response_error = client.patch("/api/update", json=error_json)
    assert response_error.status_code == 404
    assert response_error.json() == {"detail": "Assessment not found"}
    

# /api/approve-assessment
def test_approve_assessment(
    client: TestClient,
    db: Session
    ):
    github_username = db.query(models.Users)\
        .filter(models.Users.user_id == 1)\
        .with_entities(models.Users.github_username).scalar()
    
    assessment_name = db.query(models.Assessments)\
        .filter(models.Assessments.assessment_id == 1)\
        .with_entities(models.Assessments.name).scalar()
    
    reviewer = db.query(models.Reviewers)\
        .filter(models.Reviewers.reviewer_id == 1)\
        .with_entities(models.Reviewers.user_id).scalar()

    reviewer_username = db.query(models.Users)\
        .filter(models.Users.user_id == reviewer)\
        .with_entities(models.Users.github_username).scalar()
    
    request_json = {
        "reviewer_username": reviewer_username,
        "member_username": github_username,
        "assessment_name": assessment_name
    }
    response = client.patch("/api/approve_assessment", json=request_json)
    
    assert response.status_code == 200
    assert response.json() == {"Assessment Approved": True}

    error_json = {
        "reviewer_username": "error",
        "member_username": "error",
        "assessment_name": "error"
    }

    response_error = client.patch("/api/approve_assessment", json=error_json)
    assert response_error.status_code == 404
    assert response_error.json() == {"detail": "User/Reviewer Not Found"}
    assessment_error_json = {
        "reviewer_username": reviewer_username,
        "member_username": github_username,
        "assessment_name": "error"
    }
    response_error = client.patch("/api/approve_assessment", json=assessment_error_json)
    assert response_error.status_code == 404
    assert response_error.json() == {"detail": "Assessment not found"}




# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer