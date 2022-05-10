# starting with tests for api endpoints
import random
import string
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud


def test_init(client: TestClient, db: Session):
    github_username = crud.get_user_by_id(db, 1).github_username
    assessment_name = crud.get_assessment_by_id(db, 2).name
    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # Successful query
    request_json = {
        "assessment_name": assessment_name,
        "latest_commit": commit,
        "github_username": github_username,
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 200
    data = response.json()
    assert data["Initiated"] is True
    assert type(data["User_first_name"]) == str

    # Error on initializing for a second time
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry already exists."}

    # Error for reinitializing with a different commit
    request_json["latest_commit"] = "commit123"
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry already exists."}

    # Error for initializing with an incorrect username
    request_json = {
        "assessment_name": assessment_name,
        "latest_commit": commit,
        "github_username": "error",
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    # Error for initializing with an incorrect assessment name
    github_username = crud.get_user_by_id(db, 2).github_username
    request_json = {
        "assessment_name": "error",
        "latest_commit": commit,
        "github_username": github_username,
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}


def test_view(client: TestClient, db: Session):
    user_id = 1
    assessment_id = 2
    github_username = crud.get_user_by_id(db, user_id).github_username
    assessment_name = crud.get_assessment_by_id(db, assessment_id).name

    ## Successful query
    request_json = {
        "assessment_name": assessment_name,
        "github_username": github_username,
    }
    response = client.get("/api/view", json=request_json)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Initiated"
    assert data["user_id"] == user_id
    assert data["assessment_id"] == assessment_id

    ## Error on invalid username
    request_json = {
        "assessment_name": assessment_name,
        "github_username": "error",
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    ## Error on invalid assessment name
    request_json = {
        "assessment_name": "error",
        "github_username": github_username,
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}

    ## Error on missing entry
    assessment_id = 3
    assessment_name = crud.get_assessment_by_id(db, assessment_id).name
    request_json = {
        "assessment_name": assessment_name,
        "github_username": github_username,
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}


def test_delete(client: TestClient, db: Session):
    user_id = 1
    assessment_id = 3
    github_username = crud.get_user_by_id(db, user_id).github_username
    assessment_name = crud.get_assessment_by_id(db, assessment_id).name
    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    # Create entry
    request_json = {
        "assessment_name": assessment_name,
        "github_username": github_username,
        "latest_commit": commit,
    }
    response = client.post("/api/init", json=request_json)

    ## Success: Delete entry
    request_json = {
        "assessment_name": assessment_name,
        "github_username": github_username,
    }
    response = client.post("/api/delete", json=request_json)
    assert response.status_code == 200
    with pytest.raises(Exception) as exc:
        crud.get_assessment_tracker_entry(db, user_id, assessment_id)
    assert str(exc.value) == "Assessment tracker entry unavailable."

    ## Error: Delete entry that does not exist
    request_json = {
        "assessment_name": assessment_name,
        "github_username": github_username,
    }
    response = client.post("/api/delete", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}

    ## Error: Delete entry with incorrect username
    request_json = {
        "assessment_name": assessment_name,
        "github_username": "error",
    }
    response = client.post("/api/delete", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    ## Error: Delete entry with incorrect assessment name
    request_json = {
        "assessment_name": "error",
        "github_username": github_username,
    }
    response = client.post("/api/delete", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}


def test_check(client: TestClient, db: Session):

    ## Successful query
    user = crud.get_user_by_id(db, 1)
    assessment = crud.get_assessment_by_id(db, 2)
    request_json = {
        "github_username": user.github_username,
        "assessment_name": assessment.name,
        "latest_commit": "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        ),
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"Check": True}

    ## Error on username
    request_json = {
        "github_username": "error",
        "assessment_name": assessment.name,
        "latest_commit": "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        ),
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    ## Error on assessment name
    request_json = {
        "github_username": user.github_username,
        "assessment_name": "error",
        "latest_commit": "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        ),
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}

    ## Error on not initiated
    user = crud.get_user_by_id(db, 1)
    assessment = crud.get_assessment_by_id(db, 3)
    request_json = {
        "github_username": user.github_username,
        "assessment_name": assessment.name,
        "latest_commit": "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        ),
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}

    ## Error on already approved
    user = crud.get_user_by_id(db, 1)
    assessment = crud.get_assessment_by_id(db, 2)
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db, user.user_id, assessment.assessment_id
    )
    assessment_tracker_entry.status = "Approved"
    db.add(assessment_tracker_entry)
    db.commit()
    request_json = {
        "github_username": user.github_username,
        "assessment_name": assessment.name,
        "latest_commit": "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        ),
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment already approved"}
    # Revert back to initial state for subsequent tests
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db, user.user_id, assessment.assessment_id
    )
    assessment_tracker_entry.status = "Initiated"
    db.add(assessment_tracker_entry)
    db.commit()


def test_review(client: TestClient, db: Session):

    ## Success: The repo is passing checks
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 6)
    # Therefore, successful query
    request_json = {
        "commit": assessment_tracker_entry.latest_commit,
    }
    response = client.post("/api/review", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"reviewer_id": 1, "reviewer_username": "Betsy_Enos29"}

    ## Error: The repo is not passing checks
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 3)
    crud.update_assessment_log(
        db=db,
        assessment_tracker_entry_id=assessment_tracker_entry.entry_id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "Checks_passed": False,
            "Commit": assessment_tracker_entry.latest_commit,
        },
    )
    # Therefore, successful query
    request_json = {
        "commit": assessment_tracker_entry.latest_commit,
    }
    response = client.post("/api/review", json=request_json)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Automated checks not passed for latest commit"
    }

    # Error commit not found
    request_json = {
        "commit": "error",
    }
    response = client.post("/api/review", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}

    ## Error: Assessment is not at the initialization stage
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 2)
    assessment_tracker_entry.status = "Approved"
    db.add(assessment_tracker_entry)
    db.commit()
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 2)
    request_json = {
        "commit": assessment_tracker_entry.latest_commit,
    }
    response = client.post("/api/review", json=request_json)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Assessment tracker entry already under review or approved"
    }


def test_approve(client: TestClient, db: Session):

    # Tracker entry for which checks are passing
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 6)
    reviewer_id = assessment_tracker_entry.reviewer_id
    reviewer_userid = crud.get_reviewer_by_id(db, reviewer_id)
    reviewer_username = crud.get_user_by_id(db, reviewer_userid.user_id).github_username

    # Successful query
    request_json = {
        "reviewer_username": reviewer_username,
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.patch("/api/approve", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"Assessment Approved": True}
    db.refresh(assessment_tracker_entry)
    assert assessment_tracker_entry.status == "Approved"

    # Error on incorrect reviewer username
    request_json = {
        "reviewer_username": "error",
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.patch("/api/approve", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    # Error on incorrect commit
    request_json = {
        "reviewer_username": reviewer_username,
        "latest_commit": "error",
    }
    response = client.patch("/api/approve", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}

    # Error on requesting approval for an assessment that is already approved
    request_json = {
        "reviewer_username": reviewer_username,
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.patch("/api/approve", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment is not under review."}

    # Error on commit for which checks are not passing
    assessment_tracker_entry.status = "Under review"  # Reset status
    db.add(assessment_tracker_entry)
    db.commit()
    db.refresh(assessment_tracker_entry)
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 6)
    crud.update_assessment_log(
        db=db,
        assessment_tracker_entry_id=assessment_tracker_entry.entry_id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "Checks_passed": False,
            "Commit": assessment_tracker_entry.latest_commit,
        },
    )
    request_json = {
        "reviewer_username": reviewer_username,
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.patch("/api/approve", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Last commit checks failed."}

    # Error where no reviewer is assigned to the assessment
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 1)
    request_json = {
        "reviewer_username": reviewer_username,
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.patch("/api/approve", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "No reviewer is assigned to the assessment."}


def test_update(client: TestClient, db: Session):
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 6)
    github_username = crud.get_user_by_id(
        db, assessment_tracker_entry.user_id
    ).github_username
    assessment_name = crud.get_assessment_by_id(
        db, assessment_tracker_entry.assessment_id
    ).name

    # Successful query
    log = {"Test": "Tested"}
    request_json = {
        "github_username": github_username,
        "assessment_name": assessment_name,
        "commit": assessment_tracker_entry.latest_commit,
        "log": log,
    }
    response = client.patch("/api/update", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"Logs Updated": True}

    # Incorrect assessment
    request_json = {
        "github_username": github_username,
        "assessment_name": "error",
        "commit": assessment_tracker_entry.latest_commit,
        "log": log,
    }
    response = client.patch("/api/update", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}

    # Incorrect username
    request_json = {
        "github_username": "error",
        "assessment_name": assessment_name,
        "commit": assessment_tracker_entry.latest_commit,
        "log": log,
    }
    response = client.patch("/api/update", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}


# /api/confirm-reviewer
# /api/deny-reviewer
