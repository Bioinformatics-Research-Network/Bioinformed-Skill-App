import random
import string
from sqlalchemy.orm import Session
import pytest
from app.schemas import schemas
from app import models
from app.utils import *
from app.crud.crud import *


def test_get_user_id(db: Session):

    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )

    user_id = get_user_id(db=db, username=github_username)
    assert user_id == 1


def test_get_review_id(db: Session):
    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.reviewer_id == 1)
        .with_entities(models.Reviewers.user_id)
        .first()
    )
    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == reviewer.user_id)
        .with_entities(models.Users.github_username)
        .scalar()
    )
    reviewer_id = get_reviewer_id(db=db, username=github_username)
    assert reviewer_id == 1


def test_verify_check(db: Session):
    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )

    # Fail due to missing checks
    with pytest.raises(ValueError) as exc:
        crud.verify_check(
            db=db,
            user=github_username,
            assessment_name=assessment_name,
        )
    assert "Check results not available for latest commit." in str(exc.value)

    # Checks passed
    assessment_id = get_assessment_id(db=db, assessment_name=assessment_name)
    user_id = get_user_id(db=db, username=github_username)
    commit = get_latest_commit(db=db, user_id=user_id, assessment_id=assessment_id)
    update_assessment_log(
        db=db,
        asses_track_info=schemas.check_update(
            github_username=github_username,
            assessment_name=assessment_name,
            commit=commit,
        ),
        update_logs={'Checks_passed': True, 'Commit': commit},
    )
    assert verify_check(
        db=db,
        user=github_username,
        assessment_name=assessment_name,
    )


    # Checks failed
    update_assessment_log(
        db=db,
        asses_track_info=schemas.check_update(
            github_username=github_username,
            assessment_name=assessment_name,
            commit=commit,
        ),
        update_logs={'Checks_passed': False, 'Commit': commit},
    )
    assert not verify_check(
        db=db,
        user=github_username,
        assessment_name=assessment_name,
    )


def test_get_assessment_tracker_entry(db: Session):
    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )
    username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )

    user_id = get_user_id(db=db, username=username)
    assessment_id = get_assessment_id(db=db, assessment_name=assessment_name)

    # Successful query
    tracker_entry = get_assessment_tracker_entry(
        db=db, user_id=user_id, assessment_id=assessment_id
    )
    assert tracker_entry.entry_id == 6
    assert tracker_entry.user_id == 1
    assert tracker_entry.assessment_id == 2

    # Unsuccessful query
    user_id = 0
    with pytest.raises(ValueError) as exc:
        get_assessment_tracker_entry(
            db=db, user_id=user_id, assessment_id=assessment_id
        )
    assert "Assessment entry unavailable." in str(exc.value)
  

def test_get_assessment_id(db: Session):
    assessment = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    assessment_id = get_assessment_id(db=db, assessment_name=assessment)

    assert assessment_id is not None
    assert assessment_id == 2
    assessment = "Error"
    with pytest.raises(ValueError) as exc:
        get_assessment_id(db=db, assessment_name=assessment)
    assert "Assessment does not exist" in str(exc.value)


def test_init_assessment_tracker(db: Session):
    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    assessment = schemas.assessment_tracker_init(
        assessment_name=assessment_name, latest_commit=commit
    )

    initiate_assessment = init_assessment_tracker(
        db=db, assessment_tracker=assessment, user_id=2
    )

    assert initiate_assessment.status == "Initiated"
    assert initiate_assessment.assessment_id == 2
    assert initiate_assessment.user_id == 2
    assert initiate_assessment.latest_commit == commit


def test_approve_assessment_crud(
    db: Session,
):
    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    approve_assess = approve_assessment_crud(
        db=db, user_id=1, assessment_name=assessment_name
    )

    assert approve_assess.status == "Approved"
    assert approve_assess.assessment_id == 2
    assert approve_assess.user_id == 1


def test_update_assessment_log(db: Session):

    # Get data from database & fake commit
    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )
    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )
    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # Update assessment log
    assessment = schemas.check_update(
        github_username=github_username,
        assessment_name=assessment_name,
        commit=commit,
    )
    test_log = {"Test update log": True}
    update_logs = update_assessment_log(
        db=db, asses_track_info=assessment, update_logs=test_log
    )

    assert update_logs.assessment_id == 2
    assert update_logs.user_id == 1
    assert update_logs.latest_commit == commit
    logs = list(update_logs.log)
    assert test_log in logs



