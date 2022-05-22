# starting with tests for api endpoints
import random
import string
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud


def test_init(client: TestClient, db: Session):
    username = crud.get_user_by_id(db, 1).username
    assessment_name = crud.get_assessment_by_id(db, 2).name
    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # Successful query
    request_json = {
        "assessment_name": assessment_name,
        "latest_commit": commit,
        "username": username,
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 200
    data = response.json()
    assert data["Initiated"] is True
    assert type(data["username"]) == str

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
        "username": "error",
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    # Error for initializing with an incorrect assessment name
    username = crud.get_user_by_id(db, 2).username
    request_json = {
        "assessment_name": "error",
        "latest_commit": commit,
        "username": username,
    }
    response = client.post("/api/init", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}


def test_view(client: TestClient, db: Session):
    user_id = 1
    assessment_id = 2
    username = crud.get_user_by_id(db, user_id).username
    assessment_name = crud.get_assessment_by_id(db, assessment_id).name

    ## Successful query
    request_json = {
        "assessment_name": assessment_name,
        "username": username,
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Initiated"
    assert data["user_id"] == user_id
    assert data["assessment_id"] == assessment_id

    ## Error on invalid username
    request_json = {
        "assessment_name": assessment_name,
        "username": "error",
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    ## Error on invalid assessment name
    request_json = {
        "assessment_name": "error",
        "username": username,
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}

    ## Error on missing entry
    assessment_id = 3
    assessment_name = crud.get_assessment_by_id(db, assessment_id).name
    request_json = {
        "assessment_name": assessment_name,
        "username": username,
    }
    response = client.get("/api/view", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}


def test_delete(client: TestClient, db: Session):
    user_id = 1
    assessment_id = 3
    username = crud.get_user_by_id(db, user_id).username
    assessment_name = crud.get_assessment_by_id(db, assessment_id).name
    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    # Create entry
    request_json = {
        "assessment_name": assessment_name,
        "username": username,
        "latest_commit": commit,
    }
    response = client.post("/api/init", json=request_json)

    ## Success: Delete entry
    request_json = {
        "assessment_name": assessment_name,
        "username": username,
    }
    response = client.post("/api/delete", json=request_json)
    assert response.status_code == 200
    with pytest.raises(Exception) as exc:
        crud.get_assessment_tracker_entry(
            db, user_id=user_id, assessment_id=assessment_id
        )
    assert str(exc.value) == "Assessment tracker entry unavailable."

    ## Error: Delete entry that does not exist
    request_json = {
        "assessment_name": assessment_name,
        "username": username,
    }
    response = client.post("/api/delete", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}

    ## Error: Delete entry with incorrect username
    request_json = {
        "assessment_name": assessment_name,
        "username": "error",
    }
    response = client.post("/api/delete", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}

    ## Error: Delete entry with incorrect assessment name
    request_json = {
        "assessment_name": "error",
        "username": username,
    }
    response = client.post("/api/delete", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}


def test_check(client: TestClient, db: Session):

    ## Successful query
    user = crud.get_user_by_id(db, 1)
    assessment = crud.get_assessment_by_id(db, 2)
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db, user.id, assessment.id
    )
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit,
        "passed": False,
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"Check": True}

    ## Successful query with passed checks
    user = crud.get_user_by_id(db, 1)
    assessment = crud.get_assessment_by_id(db, 2)
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db, user.id, assessment.id
    )
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit,
        "passed": True,
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"Check": True}

    ## Error on invalid commit
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit + "error",
        "passed": True,
    }
    response = client.post("/api/check", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment tracker entry unavailable."}

    ## Error on already approved
    user = crud.get_user_by_id(db, 1)
    assessment = crud.get_assessment_by_id(db, 2)
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db, user.id, assessment.id
    )
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
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db, user.id, assessment.id
    )
    assessment_tracker_entry.status = "Initiated"
    db.add(assessment_tracker_entry)
    db.commit()


def test_review(client: TestClient, db: Session):

    ## Success: The repo is passing checks
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 6)
    print(assessment_tracker_entry.user_id)
    print(assessment_tracker_entry.reviewer_id)
    # Therefore, successful query
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.post("/api/review", json=request_json)
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {
        "reviewer_id": 5,
        "reviewer_username": "Toni_Hernandez31",
    }

    ## Error: The repo is not passing checks
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 3)
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": False,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 3)
    # Therefore, successful query
    request_json = {
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.post("/api/review", json=request_json)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Automated checks not passed for latest commit"
    }

    # Error commit not found
    request_json = {
        "latest_commit": "error",
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
        "latest_commit": assessment_tracker_entry.latest_commit,
    }
    response = client.post("/api/review", json=request_json)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Assessment tracker entry already under review or approved"
    }


def test_approve(client: TestClient, db: Session):

    # Tracker entry for which checks are passing
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 6)
    # Set the assessment to be "Test"
    orig_assessment_id = assessment_tracker_entry.assessment_id
    assessment_tracker_entry.assessment_id = 6
    db.commit()
    reviewer_id = assessment_tracker_entry.reviewer_id
    print(reviewer_id)
    reviewer_userid = crud.get_reviewer_by_id(db, reviewer_id=reviewer_id)
    print(reviewer_userid)
    reviewer_username = crud.get_user_by_id(
        db, user_id=reviewer_userid.user_id
    ).username
    print(reviewer_username)

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
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": False,
            "commit": assessment_tracker_entry.latest_commit,
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

    # Reset the assessment tracker entry #6 to its original assessment
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db, 6)
    assessment_tracker_entry.assessment_id = orig_assessment_id
    db.commit()


def test_update(client: TestClient, db: Session):
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, entry_id=6
    )
    username = crud.get_user_by_id(
        db, user_id=assessment_tracker_entry.user_id
    ).username
    assessment_name = crud.get_assessment_by_id(
        db, assessment_id=assessment_tracker_entry.assessment_id
    ).name

    # Successful query
    log = {"Test": "Tested"}
    request_json = {
        "username": username,
        "assessment_name": assessment_name,
        "latest_commit": assessment_tracker_entry.latest_commit,
        "log": log,
    }
    response = client.patch("/api/update", json=request_json)
    assert response.status_code == 200
    assert response.json() == {"Logs Updated": True}

    # Incorrect assessment
    request_json = {
        "username": username,
        "assessment_name": "error",
        "latest_commit": assessment_tracker_entry.latest_commit,
        "log": log,
    }
    response = client.patch("/api/update", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "Assessment does not exist"}

    # Incorrect username
    request_json = {
        "username": "error",
        "assessment_name": assessment_name,
        "latest_commit": assessment_tracker_entry.latest_commit,
        "log": log,
    }
    response = client.patch("/api/update", json=request_json)
    assert response.status_code == 422
    assert response.json() == {"detail": "User name does not exist"}


# /api/confirm-reviewer
# /api/deny-reviewer
