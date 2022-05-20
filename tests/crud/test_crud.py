import random
import string
from sqlalchemy.orm import Session
import pytest
import copy
from app import crud, schemas, models, utils


def test_get_user_by_username(db: Session):

    ## Success
    username = (
        db.query(models.Users)
        .filter(models.Users.id == 1)
        .with_entities(models.Users.username)
        .scalar()
    )

    id = crud.get_user_by_username(db=db, username=username).id
    assert id == 1

    ## Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_user_by_username(db=db, username="")
    assert "User name does not exist" in str(exc.value)


def test_get_user_by_id(db: Session):
    ## Success
    id = crud.get_user_by_id(db=db, user_id=1).id
    assert id == 1

    ## Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_user_by_id(db=db, user_id=0)
    assert "User ID does not exist" in str(exc.value)


def test_get_reviewer_by_username(db: Session):

    ## Success
    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.id == 1)
        .with_entities(models.Reviewers.id)
        .first()
    )
    username = (
        db.query(models.Users)
        .filter(models.Users.id == reviewer.id)
        .with_entities(models.Users.username)
        .scalar()
    )
    id = crud.get_reviewer_by_username(
        db=db, username=username
    ).id
    assert id == 1

    ## Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_reviewer_by_username(db=db, username="")
    assert "User name does not exist" in str(exc.value)


def test_get_reviewer_by_id(db: Session):
    ## Success
    id = crud.get_reviewer_by_id(db=db, reviewer_id=1).id
    assert id == 1

    ## Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_reviewer_by_id(db=db, reviewer_id=0)
    assert "Reviewer does not exist" in str(exc.value)


def test_get_assessment_by_name(db: Session):
    ## Success
    assessment_name = (
        db.query(models.Assessments)
        .filter(models.Assessments.id == 1)
        .with_entities(models.Assessments.name)
        .scalar()
    )
    assessment = crud.get_assessment_by_name(db=db, assessment_name=assessment_name)
    assert assessment.id == 1
    assert assessment.name == assessment_name

    ## Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_assessment_by_name(db=db, assessment_name="")
    assert "Assessment does not exist" in str(exc.value)


def test_get_assessment_by_id(db: Session):
    ## Success
    assessment = crud.get_assessment_by_id(db=db, assessment_id=3)
    assert assessment.id == 3

    ## Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_assessment_by_id(db=db, assessment_id=0)
    assert "Assessment ID does not exist" in str(exc.value)


def test_get_assessment_tracker_entry(db: Session):
    user = crud.get_user_by_id(db=db, entry_id=1)
    assessment = crud.get_assessment_by_id(db=db, entry_id=2)

    ## Successful query
    tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )
    assert tracker_entry.id == 6
    assert tracker_entry.id == 1
    assert tracker_entry.id == 2

    ## Unsuccessful query
    id = 0
    with pytest.raises(ValueError) as exc:
        crud.get_assessment_tracker_entry(
            db=db, user_id=id, assessment_id=assessment.id
        )
    assert "Assessment tracker entry unavailable." in str(exc.value)


def test_init_assessment_tracker(db: Session):
    assessment = crud.get_assessment_by_id(db=db, assessment_id=3)
    user = crud.get_user_by_id(db=db, user_id=3)
    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    init_request = schemas.InitRequest(
        assessment_name=assessment.name,
        username=user.username,
        latest_commit=commit,
    )
    initiate_assessment = crud.init_assessment_tracker(
        db=db, init_request=init_request, user_id=user.id
    )
    assert initiate_assessment
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )
    assert assessment_tracker_entry.status == "Initiated"
    assert assessment_tracker_entry.id == assessment.id
    assert assessment_tracker_entry.id == user.id
    assert assessment_tracker_entry.latest_commit == commit


def test_select_reviewer(db: Session):
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, entry_id=1
    )
    reviewer = crud.select_reviewer(
        db=db, assessment_tracker_entry=assessment_tracker_entry
    )
    assert reviewer.id != assessment_tracker_entry.id


def test_approve_assessment(
    db: Session,
):
    ## Successful approval
    trainee = crud.get_user_by_id(db=db, user_id=1)
    assessment = crud.get_assessment_by_id(db=db, assessment_id=2)
    reviewer = crud.get_reviewer_by_id(db=db, reviewer_id=1)
    reviewer_username = crud.get_user_by_id(
        db=db, reviewer_id=reviewer.id
    ).username
    # Ensure checks are passed
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": True,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    # Approve assessment
    approve_assess = crud.approve_assessment(
        db=db,
        trainee=trainee,
        assessment=assessment,
        reviewer=reviewer,
        reviewer_username=reviewer_username,
    )
    assert approve_assess
    # Verify that the assessment is approved
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )
    assert assessment_tracker_entry.status == "Approved"
    assert assessment_tracker_entry.id == 2
    assert assessment_tracker_entry.id == 1

    ## Unsuccessful approval
    ## Due to no reviewer assigned
    assessment = crud.get_assessment_by_id(db=db, assessment_id=4)
    with pytest.raises(ValueError) as exc:
        crud.approve_assessment(
            db=db,
            trainee=trainee,
            assessment=assessment,
            reviewer=reviewer,
            reviewer_username=reviewer_username,
        )
    assert "No reviewer is assigned to the assessment." in str(exc.value)
    # Verify that the assessment is not approved
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )
    assert assessment_tracker_entry.status != "Approved"
    assert assessment_tracker_entry.id == 4
    assert assessment_tracker_entry.id == 1

    ## Unsuccessful approval
    ## Due to checks failing
    # Refresh status to be "Under review"
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, entry_id=6
    )
    assessment_tracker_entry.status = "Under review"  # Reset status
    db.add(assessment_tracker_entry)
    db.commit()
    db.refresh(assessment_tracker_entry)
    # Update logs to fail checks
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, entry_id=6
    )
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": False,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    # Approve assessment
    trainee = crud.get_user_by_id(db=db, assessment_id=assessment_tracker_entry.id)
    reviewer = crud.get_reviewer_by_id(
        db=db, assessment_id=assessment_tracker_entry.id
    )
    reviewer_username = crud.get_user_by_id(
        db=db, reviewer_id=reviewer.id
    ).username
    assessment = crud.get_assessment_by_id(
        db=db, assessment_id=assessment_tracker_entry.id
    )
    with pytest.raises(ValueError) as exc:
        crud.approve_assessment(
            db=db,
            trainee=trainee,
            assessment=assessment,
            reviewer=reviewer,
            reviewer_username=reviewer_username,
        )
    assert "Last commit checks failed." in str(exc.value)

    ## Unsuccessful approval
    ## Due to reviewer being same as trainee
    reviewer = crud.get_reviewer_by_id(db=db, reviewer_id=2)
    reviewer_username = crud.get_user_by_id(
        db=db, reviewer_id=reviewer.id
    ).username
    with pytest.raises(ValueError) as exc:
        crud.approve_assessment(
            db=db,
            trainee=trainee,
            assessment=assessment,
            reviewer=reviewer,
            reviewer_username=reviewer_username,
        )
    assert "Reviewer cannot be the same as the trainee." in str(exc.value)

    ## Unsuccessful approval
    ## Due to reviewer being different from the assessment tracker record
    # Update logs to pass checks
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, entry_id=6
    )
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": True,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, entry_id=6
    )
    reviewer = crud.get_reviewer_by_id(db=db, reviewer_id=4)
    reviewer_username = crud.get_user_by_id(
        db=db, reviewer_id=reviewer.id
    ).username
    with pytest.raises(ValueError) as exc:
        crud.approve_assessment(
            db=db,
            trainee=trainee,
            assessment=assessment,
            reviewer=reviewer,
            reviewer_username=reviewer_username,
        )
    assert (
        "Reviewer is not the same as the reviewer assigned to the assessment."
        in str(exc.value)
    )


def test_update_assessment_log(db: Session):

    # Get data from database & fake commit
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=1, assessment_id=2
    )
    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # Update assessment log
    test_log = {"Test update log": True}
    update_logs = crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=commit,
        update_logs=copy.deepcopy(test_log),
    )
    assert update_logs
    # Verify that the log is updated
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=1, assessment_id=2
    )
    assert assessment_tracker_entry.id == 2
    assert assessment_tracker_entry.id == 1
    assert assessment_tracker_entry.latest_commit == commit
    logs = list(assessment_tracker_entry.log)
    assert logs[-1]["Test update log"]

    ## Unsuccessful update
    ## Due to incorrect assessment tracker ID
    with pytest.raises(ValueError) as exc:
        crud.update_assessment_log(
            db=db,
            entry_id=0,
            latest_commit=commit,
            update_logs=copy.deepcopy(test_log),
        )
    assert "Assessment tracker entry unavailable." in str(exc.value)
