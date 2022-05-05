import random
import string
from sqlalchemy.orm import Session
from app.schemas import schemas
from app import models
from app.crud import crud


def test_verify_member(db: Session):

    github_username = (
        db.query(models.Users)
        .filter(models.Users.user_id == 1)
        .with_entities(models.Users.github_username)
        .scalar()
    )

    user = crud.verify_member(db=db, username=github_username)

    assert user is not None
    assert type(user.user_id) == int
    assert type(user.first_name) == str


def test_verify_reviewer(db: Session):
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

    reviewer_verify = crud.verify_reviewer(db=db, reviewer_username=github_username)

    assert reviewer_verify is not None
    assert reviewer_verify.reviewer_id == 1


def test_assessment_id_tracker(db: Session):
    assessment = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == 2)
        .with_entities(models.Assessments.name)
        .scalar()
    )

    assessment_id = crud.assessment_id_tracker(db=db, assessment_name=assessment)

    assert assessment_id is not None
    assert assessment_id == 2
    assessment = "Error"
    assessment_id = crud.assessment_id_tracker(db=db, assessment_name=assessment)
    assert assessment_id is None


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

    initiate_assessment = crud.init_assessment_tracker(
        db=db, assessment_tracker=assessment, user_id=1
    )

    assert initiate_assessment.status == "Initiated"
    assert initiate_assessment.assessment_id == 2
    assert initiate_assessment.user_id == 1
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

    approve_assess = crud.approve_assessment_crud(
        db=db, user_id=1, assessment_name=assessment_name
    )

    assert approve_assess.status == "Approved"
    assert approve_assess.assessment_id == 2
    assert approve_assess.user_id == 1


def test_update_assessment_log(db: Session):
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

    assessment = schemas.check_update(
        github_username=github_username,
        assessment_name=assessment_name,
        commit=commit,
    )
    test_log = {"Test update log": True}
    update_logs = crud.update_assessment_log(
        db=db, asses_track_info=assessment, update_logs=test_log
    )

    assert update_logs.assessment_id == 2
    assert update_logs.user_id == 1
    assert update_logs.latest_commit == commit
    logs = list(update_logs.log)
    assert test_log in logs
