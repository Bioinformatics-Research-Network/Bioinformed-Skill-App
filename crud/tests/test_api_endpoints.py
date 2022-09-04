# starting with tests for api endpoints
import random
import string
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud
import app.db.models as models
from app.dependencies import Settings, get_db


def test_init(client: TestClient, db: Session):

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # get a user where username is brnbot
    user = db.query(models.Users).filter(models.Users.username == "bioresnet").first()

    # Check if the assessment tracker entry exists
    tracker_entry = db.query(models.AssessmentTracker).filter(
        models.AssessmentTracker.assessment_id == assessment.id,
        models.AssessmentTracker.user_id == user.id,
    ).first()
    if tracker_entry is not None:
        # Get any assertions tied to this entry
        assertions = db.query(models.Assertions).filter(
            models.Assertions.assessment_tracker_id == tracker_entry.id
        ).all()
        # Delete all assertions tied to this entry
        for assertion in assertions:
            db.delete(assertion)
        db.delete(tracker_entry)
        db.commit()

    # Successful query
    request_json = {
        "user_id": user.id,
        "assessment_id": assessment.id,
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 200
    assert response.json()

    # Error on initializing for a second time
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Assessment tracker entry already exists."
    }

    # Error for initializing with an incorrect user
    request_json = {
        "user_id": 0,
        "assessment_id": assessment.id,
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User ID does not exist"}

    # Error for initializing with an incorrect assessment name
    request_json = {
        "user_id": user.id,
        "assessment_id": 0,
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment ID does not exist"}


def test_view(client: TestClient, db: Session):

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # get a user where username is brnbot
    user = db.query(models.Users).filter(models.Users.username == "bioresnet").first()

    # Successful query
    request_json = {
        "assessment_name": assessment.name,
        "username": user.username,
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Initiated"
    assert data["user_id"] == user.id
    assert data["assessment_id"] == assessment.id

    # Error on invalid username
    request_json = {
        "assessment_name":  assessment.name,
        "username": "error",
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    # Error on invalid assessment name
    request_json = {
        "assessment_name": "error",
        "username": user.username,
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}

    # Error on missing entry
    request_json = {
        "assessment_name": assessment.name,
        "username": "errorbot",
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}


def test_check(client: TestClient,  db: Session):

    db = next(get_db())

    # For some reason, we have to retrieve the db session again
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()
    user = db.query(models.Users).filter(models.Users.username == "bioresnet").first()
    assessment_tracker_entry = db.query(models.AssessmentTracker).filter(
        models.AssessmentTracker.assessment_id == assessment.id,
        models.AssessmentTracker.user_id == user.id,
    ).first()
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )

    # Successful query
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit,
        "passed": False,
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"Check": True, "review_required": True}

    # Error on invalid commit
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit + "error",
        "passed": True,
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}

    # Error on already approved
    assessment_tracker_entry.status = "Approved"
    db.add(assessment_tracker_entry)
    db.commit()
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit,
        "passed": True,
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment already approved"}

    # Revert back to initial state for subsequent tests
    assessment_tracker_entry.status = "Initiated"
    db.add(assessment_tracker_entry)
    db.commit()
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db, user.id, assessment.id
    )
    assert assessment_tracker_entry.status == "Initiated"


def test_review(client: TestClient, db: Session):

    # For some reason, we have to retrieve the db session again
    db = next(get_db())
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()
    user = db.query(models.Users).filter(models.Users.username == "bioresnet").first()
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )

    # Success: The repo is passing checks
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit,
        "passed": True,
    }
    response = client.post("/api/check", json=request_json)
    # Therefore, successful reviewer query
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.post("/api/review", json=request_json)
    assert response.status_code == 200


def test_approve(client: TestClient, db: Session):

    db = next(get_db())

    # For some reason, we have to retrieve the db session again
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()
    user = db.query(models.Users).filter(models.Users.username == "bioresnet").first()
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )
    reviewer = crud.get_reviewer_by_id(
        db=db, reviewer_id=assessment_tracker_entry.reviewer_id
    )
    revuser = crud.get_user_by_id(db=db, user_id=reviewer.user_id)

    # Successful query
    request_json = {
        "reviewer_username": revuser.username,
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.patch("/api/approve", json=request_json)

    # Badge is missing
    # TODO: Fix this so that it produces a 200 response
    assert response.status_code == 422


def test_update(client: TestClient, db: Session):
    db = next(get_db())

    # For some reason, we have to retrieve the db session again
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()
    user = db.query(models.Users).filter(models.Users.username == "bioresnet").first()
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )

    # Successful query
    log = {"Test": "Tested"}
    request_json = {
        "username": user.username,
        "assessment_name": assessment.name,
        "latest_commit": assessment_tracker_entry.latest_commit,
        "log": log,
    }
    response = client.patch("/api/update", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"Logs Updated": True}

