import random
import string
from sqlalchemy.orm import Session
import pytest
import copy
from app import crud, utils
import app.db.models as models
from app.dependencies import settings
from sqlalchemy.exc import IntegrityError
import time
from datetime import datetime

# Set random seed based on current time
random.seed(time.time())


def test_get_user_by_username(db: Session):

    # Get a valid user
    user = db.query(models.Users).first()

    # Success
    username = crud.get_user_by_username(db=db, username=user.username).username
    assert username == user.username

    # Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_user_by_username(db=db, username="")
    assert "User name does not exist" in str(exc.value)


def test_get_user_by_id(db: Session):

    # Get a valid user
    user = db.query(models.Users).first()

    # Success
    id = crud.get_user_by_id(db=db, user_id=user.id).id
    assert id == user.id

    # Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_user_by_id(db=db, user_id=0)
    assert "User ID does not exist" in str(exc.value)


def test_get_reviewer_by_username(db: Session):

    # get a valid reviewer
    reviewer = db.query(models.Reviewers).first()
    # Success
    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.id == reviewer.id)
        .first()
    )
    username = (
        db.query(models.Users)
        .filter(models.Users.id == reviewer.user_id)
        .with_entities(models.Users.username)
        .scalar()
    )
    reviewer_id = crud.get_reviewer_by_username(db=db, username=username).id
    assert reviewer_id == reviewer.id

    # Unsuccessful - reviewer does not exist as a user
    with pytest.raises(ValueError) as exc:
        crud.get_reviewer_by_username(db=db, username="")
    assert "User name does not exist" in str(exc.value)

    # Unsuccessful - selected reviewer is a user but not a reviewer
    # First, get all reviewers
    reviewers = db.query(models.Reviewers).all()
    # Then, get a random user who is not in the list of reviewers
    user = (
        db.query(models.Users)
        .filter(
            models.Users.id.notin_([reviewer.user_id for reviewer in reviewers])
        )
        .first()
    )
    # Raise an error when attempting to get a reviewer by username
    with pytest.raises(ValueError) as exc:
        crud.get_reviewer_by_username(db=db, username=user.username)
    assert "Reviewer does not exist" in str(exc.value)


def test_get_reviewer_by_id(db: Session):

    # get a valid reviewer
    reviewer = db.query(models.Reviewers).first()

    # Success
    id = crud.get_reviewer_by_id(db=db, reviewer_id=reviewer.id).id
    assert id == reviewer.id

    # Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_reviewer_by_id(db=db, reviewer_id=0)

    assert "Reviewer does not exist" in str(exc.value)


def test_get_assessment_by_name(db: Session):

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # Success
    assessment_q = crud.get_assessment_by_name(
        db=db, assessment_name=assessment.name
    )
    assert assessment_q.id == assessment.id
    assert assessment_q.name == assessment.name

    # Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_assessment_by_name(db=db, assessment_name="")
    assert "Assessment does not exist" in str(exc.value)


def test_get_assessment_by_id(db: Session):

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # Success
    assessment_q = crud.get_assessment_by_id(db=db, assessment_id=assessment.id)
    assert assessment_q.id == assessment.id

    # Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_assessment_by_id(db=db, assessment_id=0)

    assert "Assessment ID does not exist" in str(exc.value)


def test_get_assessment_tracker_entry(db: Session):

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # Get a valid user
    user = db.query(models.Users).first()

    # Create an assessment tracker entry if it doesnt' exist
    try:
        tracker_entry = crud.get_assessment_tracker_entry(
            db=db, user_id=user.id, assessment_id=assessment.id
        )
    except Exception:
        assessment_tracker_entry = models.AssessmentTracker(
            assessment_id=assessment.id, user_id=user.id, latest_commit='sdjad8j', log={}, status="init"
        )
        db.add(assessment_tracker_entry)
        db.commit()

    # Successful query
    tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )
    assert tracker_entry.user_id == user.id
    assert tracker_entry.assessment_id == assessment.id

    # Unsuccessful query
    user_id = 0
    with pytest.raises(ValueError) as exc:
        crud.get_assessment_tracker_entry(
            db=db, user_id=user_id, assessment_id=assessment.id
        )
    assert "Assessment tracker entry unavailable." in str(exc.value)


def test_init_assessment_tracker(db: Session):

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # get a user where username is brnbot
    user = db.query(models.Users).filter(models.Users.username == "brnbot").first()

    commit = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=20)
    )

    # Check if the assessment tracker entry exists
    tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )
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

    # Init assessment tracker
    crud.create_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id, commit=commit
    )

    # Get the entry
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )

    # Check that the entry is correct
    assert assessment_tracker_entry.status == "Pre-assessment"
    assert assessment_tracker_entry.assessment_id == assessment.id
    assert assessment_tracker_entry.user_id == user.id
    assert assessment_tracker_entry.latest_commit == commit


def test_select_reviewer(db: Session):

    # get a valid assessment tracker entry
    assessment_tracker_entry = db.query(models.AssessmentTracker).first()

    # Success
    reviewer = crud.select_reviewer(
        db=db, assessment_tracker_entry=assessment_tracker_entry, settings=settings
    )
    assert reviewer.user_id != assessment_tracker_entry.user_id


def test_approve_assessment(
    db: Session,
):
    # get a user where username is brnbot
    trainee = db.query(models.Users).filter(models.Users.username == "brnbot").first()

    # Get a user where username is brnbot2
    revuser = db.query(models.Users).filter(models.Users.username == "brnbot2").first()

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # Get the reviewer info for brnbot2
    reviewer = db.query(models.Reviewers).filter(models.Reviewers.user_id == revuser.id).first()

    # Get reviewer username
    reviewer_username = db.query(models.Users).filter(models.Users.id == reviewer.user_id).first().username

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

    # Set assessment tracker entry to be under review
    # And set reviewer
    assessment_tracker_entry.status = "Under review"
    assessment_tracker_entry.reviewer_id = reviewer.id
    db.commit()

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

    # Unsuccessful approval
    # Due to not being under review
    with pytest.raises(ValueError) as exc:
        crud.approve_assessment(
            db=db,
            trainee=trainee,
            assessment=assessment,
            reviewer=reviewer,
            reviewer_username=reviewer_username,
        )
    assert "Assessment is not under review." in str(exc.value)

    # Dut to no reviewer assigned
    assessment_tracker_entry.status = "Under review"
    assessment_tracker_entry.reviewer_id = None
    db.commit()
    # Set checks to be passed
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": True,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
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

    # Unsuccessful approval
    # Due to checks failing
    # Refresh status to be "Under review"
    assessment_tracker_entry.status = "Under review"  # Reset status
    db.commit()
    # Update logs to fail checks
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
    with pytest.raises(ValueError) as exc:
        crud.approve_assessment(
            db=db,
            trainee=trainee,
            assessment=assessment,
            reviewer=reviewer,
            reviewer_username=reviewer_username,
        )
    assert "Last commit checks failed." in str(exc.value)

    # Unsuccessful approval
    # Due to reviewer being different from the assessment tracker record
    # Update logs to pass checks
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": True,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    # Set reviewer id
    assessment_tracker_entry.reviewer_id = reviewer.id
    # Get wrong reviewer
    reviewer = crud.get_reviewer_by_username(db=db, username="brnbot3")
    reviewer_username = crud.get_user_by_id(db=db, user_id=reviewer.user_id).username
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

    # Unsuccessful approval
    # Due to reviewer being same as trainee
    # Get reviewer who is trainee
    reviewer = crud.get_reviewer_by_user_id(db=db, user_id=trainee.id)
    reviewer_username = crud.get_user_by_id(db=db, user_id=reviewer.user_id).username
    with pytest.raises(ValueError) as exc:
        crud.approve_assessment(
            db=db,
            trainee=trainee,
            assessment=assessment,
            reviewer=reviewer,
            reviewer_username=reviewer_username,
        )
    assert "Reviewer cannot be the same as the trainee." in str(exc.value)


def test_add_assertion(db: Session):
    """Test add assertion."""

    # Get bt
    bt = utils.get_bearer_token(config=settings)

    # get a user where username is brnbot
    trainee = db.query(models.Users).filter(models.Users.username == "brnbot").first()

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # Get assessment tracker entry
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )

    # Issue the badge
    issued = utils.issue_badge(
        assessment_name=assessment.name,
        user_email=trainee.email,
        user_first="BRN",
        user_last="Bot",
        bearer_token=bt,
        config=settings,
    )
    assert issued.status_code in [200, 201]

    # Get the assertion from badgr
    resp = utils.get_assertion(
        assessment_name=assessment.name,
        user_email=trainee.email,
        bearer_token=bt, 
        config=settings
    )
    assert resp.status_code in [200, 201]
    assert resp.json()["status"] == {'success': True, 'description': 'ok', 'fieldErrors': None, 'validationErrors': None}

    assertion = resp.json()["result"][0]

    # Query for a badge where entityId is settings.BADGE_IDs['Test']
    badge = db.query(models.Badges).filter(models.Badges.entityId == settings.BADGE_IDs['Test']).first()
    if badge is None:
        print("Adding test badge to db")
        badges = utils.get_all_badges(bearer_token=bt, config=settings)
        badge = badges.json()["result"][0]
        # Convert all the fields to strings using dict comprehension and format time
        fields = {k: str(v) for k, v in badge.items()}
        fields["createdAt"] = datetime.strptime(fields["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        # Add to db
        print("Badge does not exist in database")
        badge = models.Badges(**fields)
        db.add(badge)
        db.commit()
    
    # Get assertion from db and delete if it exists
    assertion_db = db.query(models.Assertions).filter(
        models.Assertions.assessment_tracker_id == assessment_tracker_entry.id
    ).first()
    if assertion_db is not None:
        # Delete assertion from db
        db.delete(assertion_db)
        db.commit()

    # Add assertion
    res = crud.add_assertion(
        db=db, assertion=assertion, entry_id=assessment_tracker_entry.id
    )
    assert res

    # Fail on second add
    with pytest.raises(IntegrityError) as exc:
        crud.add_assertion(
            db=db, assertion=assertion, entry_id=assessment_tracker_entry.id
        )


def test_update_assessment_log(db: Session):

    # get a user where username is brnbot
    trainee = db.query(models.Users).filter(models.Users.username == "brnbot").first()

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # Get assessment tracker entry
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )

    commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=25))

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
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )
    assert assessment_tracker_entry.assessment_id == assessment.id
    assert assessment_tracker_entry.user_id == trainee.id
    assert assessment_tracker_entry.latest_commit == commit
    logs = list(assessment_tracker_entry.log)
    assert logs[-1]["Test update log"]

    # Unsuccessful update
    # Due to incorrect assessment tracker ID
    with pytest.raises(ValueError) as exc:
        crud.update_assessment_log(
            db=db,
            entry_id=0,
            latest_commit=commit,
            update_logs=copy.deepcopy(test_log),
        )
    assert "Assessment tracker entry unavailable." in str(exc.value)
