# starting with tests for api endpoints
from datetime import datetime
import random
import string
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models


# /api/init-assessment
def test_init_assessment(client: TestClient, db: Session):
    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )

    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    request_json = {
        "user": {"github_username": github_username},
        "assessment_tracker": {
            "assessment_name": assessment_name,
            "latest_commit": "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            ),
        },
    }
    response = client.post("/api/init_assessment", json=request_json)

    assert response.status_code == 200
    data = response.json()
    assert data["Initiated"] is True
    assert type(data["User_first_name"]) == str

    error_json = {
        "user": {"github_username": "errorhandling"},
        "assessment_tracker": {
            "assessment_name": "error",
            "latest_commit": "errors",
        },
    }
    response_error = client.post("/api/init_assessment", json=error_json)

    assert response_error.status_code == 422
    assert response_error.json() == {"detail": "User not found"}
    error_json_2 = {
        "user": {"github_username": github_username},
        "assessment_tracker": {
            "assessment_name": "error",
            "latest_commit": "string",
        },
    }
    response_error = client.post("/api/init_assessment", json=error_json_2)

    assert response_error.status_code == 422
    assert response_error.json() == {"detail": "Invalid Assessment name"}


# /api/init-check
def test_init_check(client: TestClient, db: Session):
    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )
    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    request_json = {
        "github_username": github_username,
        "assessment_name": assessment_name,
        "commit": "".join(random.choices(string.ascii_uppercase + string.digits, k=10)),
    }

    response = client.post("/api/init_check", json=request_json)

    assert response.status_code == 200
    assert response.json() == {"Logs updated": "init-check"}
    error_json = {
        "github_username": "error",
        "assessment_name": "error",
        "commit": "error",
    }
    response_error = client.post("/api/init_check", json=error_json)
    assert response_error.status_code == 422
    assert response_error.json() == {"detail": "User Not Registered"}


# /api/update
def test_update(client: TestClient, db: Session):
    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )

    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    logs = {"Updated": str(datetime.utcnow()), "Commit": commit}
    request_json = {
        "asses_track_info": {
            "github_username": github_username,
            "assessment_name": assessment_name,
            "commit": commit,
        },
        "update_logs": {"log": logs},
    }

    response = client.patch("/api/update", json=request_json)

    assert response.status_code == 200
    assert response.json() == {"Logs Updated": "update"}
    assessment_error = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 1)
        .with_entities(models.Assessments.name)
        .scalar()
    )
    error_json = {
        "asses_track_info": {
            "github_username": github_username,
            "assessment_name": assessment_error,
            "commit": "error",
        },
        "update_logs": {"log": {"Error": "update log"}},
    }
    response_error = client.patch("/api/update", json=error_json)
    assert response_error.status_code == 422
    assert response_error.json() == {"detail": "Assessment not found"}
    error_json = {
        "asses_track_info": {
            "github_username": "error",
            "assessment_name": assessment_name,
            "commit": "error",
        },
        "update_logs": {"log": {"Error": "update log"}},
    }
    response_error = client.patch("/api/update", json=error_json)
    assert response_error.status_code == 422
    assert response_error.json() == {"detail": "Assessment not found"}


# /api/approve-assessment
def test_approve_assessment(client: TestClient, db: Session):
    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )

    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.user_id != 1)
        .with_entities(models.Reviewers.user_id)
        .first()
    )

    reviewer_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == reviewer.user_id)
        .with_entities(models.Users.github_username)
        .scalar()
    )

    request_json = {
        "reviewer_username": reviewer_username,
        "member_username": github_username,
        "assessment_name": assessment_name,
    }
    response = client.patch("/api/approve_assessment", json=request_json)

    assert response.status_code == 200
    assert response.json() == {"Assessment Approved": True}

    error_json = {
        "reviewer_username": "error",
        "member_username": "error",
        "assessment_name": assessment_name,
    }

    response_error = client.patch("/api/approve_assessment", json=error_json)
    assert response_error.status_code == 422
    assert response_error.json() == {"detail": "User/Reviewer Not Found"}

    assessment_error = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 1)
        .with_entities(models.Assessments.name)
        .scalar()
    )
    assessment_error_json = {
        "reviewer_username": reviewer_username,
        "member_username": github_username,
        "assessment_name": assessment_error,
    }
    response_error = client.patch("/api/approve_assessment", json=assessment_error_json)
    assert response_error.status_code == 422
    assert response_error.json() == {"detail": "Assessment not found"}
    assessment_error_json = {
        "reviewer_username": reviewer_username,
        "member_username": github_username,
        "assessment_name": "errorid",
    }
    response_error = client.patch("/api/approve_assessment", json=assessment_error_json)
    assert response_error.status_code == 422
    assert response_error.json() == {"detail": "Assessment not found"}
    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.reviewer_id == 1)
        .with_entities(models.Reviewers.user_id)
        .scalar()
    )
    reviewer_username_error = (
        db.query(models.Users)
        .filter(models.Users.user_id == reviewer)
        .with_entities(models.Users.github_username)
        .scalar()
    )
    github_username_error = (
        db.query(models.Users)
        .filter(models.Users.user_id == reviewer)
        .with_entities(models.Users.github_username)
        .scalar()
    )
    assessment_error_json = {
        "reviewer_username": reviewer_username_error,
        "member_username": github_username_error,
        "assessment_name": assessment_name,
    }
    response_error = client.patch("/api/approve_assessment", json=assessment_error_json)
    assert response_error.status_code == 422
    assert response_error.json() == {
        "detail": "Reviewer not authorized to review personal assessments"
    }


# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
