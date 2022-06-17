import random
import string
from sqlalchemy.orm import Session
import pytest
import copy
from app import crud, utils
import app.db.models as models
import app.api.schemas as schemas
from app.dependencies import settings
from sqlalchemy.exc import IntegrityError


def test_get_user_by_username(db: Session):

    # Get a valid user
    user = db.query(models.Users).first()

    # Success
    print(user)
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

    # get a valid assessment
    assessment = db.query(models.Assessments).first()

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

    # get a valid assessment
    assessment = db.query(models.Assessments).first()

    # Success
    assessment_q = crud.get_assessment_by_id(db=db, assessment_id=assessment.id)
    assert assessment_q.id == assessment.id

    # Unsuccessful
    with pytest.raises(ValueError) as exc:
        crud.get_assessment_by_id(db=db, assessment_id=0)

    assert "Assessment ID does not exist" in str(exc.value)


def test_get_assessment_tracker_entry(db: Session):

    # get a valid assessment
    assessment = db.query(models.Assessments).first()

    # Get a valid user
    user = db.query(models.Users).first()

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

    # get a valid assessment
    assessment = db.query(models.Assessments).first()

    # Get a valid user
    user = db.query(models.Users).first()

    commit = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=10)
    )

    # Check if the assessment tracker entry exists
    try:
        tracker_entry = crud.get_assessment_tracker_entry(
            db=db, user_id=user.id, assessment_id=assessment.id
        )
        db.delete(tracker_entry)
        db.commit()
    except ValueError:
        print("Assessment tracker entry does not exist... creating.")

    # Init assessment tracker
    initiate_assessment = crud.create_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id, commit=commit
    )

    assert initiate_assessment

    # Get the entry
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )

    # Check that the entry is correct
    assert assessment_tracker_entry.status == "Pre-assessment"
    assert assessment_tracker_entry.assessment_id == assessment.id
    assert assessment_tracker_entry.user_id == user.id
    assert assessment_tracker_entry.latest_commit == commit


# def test_select_reviewer(db: Session):
#     assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
#         db=db, entry_id=1
#     )

#     # Success
#     reviewer = crud.select_reviewer(
#         db=db, assessment_tracker_entry=assessment_tracker_entry
#     )
#     assert reviewer.user_id != assessment_tracker_entry.user_id

#     # Success with no invalid reviewers
#     assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
#         db=db, entry_id=7
#     )
#     reviewer = crud.select_reviewer(
#         db=db, assessment_tracker_entry=assessment_tracker_entry
#     )
#     assert reviewer.user_id != assessment_tracker_entry.user_id


# def test_approve_assessment(
#     db: Session,
# ):
#     # Successful approval
#     trainee = crud.get_user_by_id(db=db, user_id=1)
#     a = trainee.__repr__  # Gets repr of user object
#     assert a is not None
#     assessment = crud.get_assessment_by_id(db=db, assessment_id=2)
#     reviewer = crud.get_reviewer_by_id(db=db, reviewer_id=1)
#     reviewer_username = crud.get_user_by_id(db=db, user_id=reviewer.user_id).username
#     # Ensure checks are passed
#     assessment_tracker_entry = crud.get_assessment_tracker_entry(
#         db=db, user_id=trainee.id, assessment_id=assessment.id
#     )
#     crud.update_assessment_log(
#         db=db,
#         entry_id=assessment_tracker_entry.id,
#         latest_commit=assessment_tracker_entry.latest_commit,
#         update_logs={
#             "checks_passed": True,
#             "commit": assessment_tracker_entry.latest_commit,
#         },
#     )
#     # Set assessment tracker entry to be under review
#     # And set reviewer
#     assessment_tracker_entry.status = "Under review"
#     assessment_tracker_entry.reviewer_id = reviewer.id
#     db.commit()
#     # Approve assessment
#     approve_assess = crud.approve_assessment(
#         db=db,
#         trainee=trainee,
#         assessment=assessment,
#         reviewer=reviewer,
#         reviewer_username=reviewer_username,
#     )
#     assert approve_assess
#     # Verify that the assessment is approved
#     assessment_tracker_entry = crud.get_assessment_tracker_entry(
#         db=db, user_id=trainee.id, assessment_id=assessment.id
#     )
#     assert assessment_tracker_entry.status == "Approved"

#     # Unsuccessful approval
#     # Due to not being under review
#     assessment = crud.get_assessment_by_id(db=db, assessment_id=5)
#     assessment_tracker_entry = crud.get_assessment_tracker_entry(
#         db=db, user_id=trainee.id, assessment_id=5
#     )
#     assessment_tracker_entry.reviewer_id = reviewer.id
#     with pytest.raises(ValueError) as exc:
#         crud.approve_assessment(
#             db=db,
#             trainee=trainee,
#             assessment=assessment,
#             reviewer=reviewer,
#             reviewer_username=reviewer_username,
#         )
#     assert "Assessment is not under review." in str(exc.value)

#     # Dut to no reviewer assigned
#     assessment_tracker_entry.status = "Under review"
#     assessment_tracker_entry.reviewer_id = None
#     db.commit()
#     # Set checks to be passed
#     crud.update_assessment_log(
#         db=db,
#         entry_id=assessment_tracker_entry.id,
#         latest_commit=assessment_tracker_entry.latest_commit,
#         update_logs={
#             "checks_passed": True,
#             "commit": assessment_tracker_entry.latest_commit,
#         },
#     )
#     with pytest.raises(ValueError) as exc:
#         crud.approve_assessment(
#             db=db,
#             trainee=trainee,
#             assessment=assessment,
#             reviewer=reviewer,
#             reviewer_username=reviewer_username,
#         )
#     assert "No reviewer is assigned to the assessment." in str(exc.value)
#     # Verify that the assessment is not approved
#     assessment_tracker_entry = crud.get_assessment_tracker_entry(
#         db=db, user_id=trainee.id, assessment_id=assessment.id
#     )
#     assert assessment_tracker_entry.status != "Approved"
#     assert assessment_tracker_entry.assessment_id == 5
#     assert assessment_tracker_entry.user_id == 1

#     # Unsuccessful approval
#     # Due to checks failing
#     # Refresh status to be "Under review"
#     assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
#         db=db, entry_id=6
#     )
#     assessment_tracker_entry.status = "Under review"  # Reset status
#     db.add(assessment_tracker_entry)
#     db.commit()
#     db.refresh(assessment_tracker_entry)
#     # Update logs to fail checks
#     assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
#         db=db, entry_id=6
#     )
#     crud.update_assessment_log(
#         db=db,
#         entry_id=assessment_tracker_entry.id,
#         latest_commit=assessment_tracker_entry.latest_commit,
#         update_logs={
#             "checks_passed": False,
#             "commit": assessment_tracker_entry.latest_commit,
#         },
#     )
#     # Approve assessment
#     trainee = crud.get_user_by_id(db=db, user_id=assessment_tracker_entry.user_id)
#     reviewer = crud.get_reviewer_by_id(
#         db=db, reviewer_id=assessment_tracker_entry.reviewer_id
#     )
#     reviewer_username = crud.get_user_by_id(db=db, user_id=reviewer.user_id).username
#     assessment = crud.get_assessment_by_id(
#         db=db, assessment_id=assessment_tracker_entry.assessment_id
#     )
#     with pytest.raises(ValueError) as exc:
#         crud.approve_assessment(
#             db=db,
#             trainee=trainee,
#             assessment=assessment,
#             reviewer=reviewer,
#             reviewer_username=reviewer_username,
#         )
#     assert "Last commit checks failed." in str(exc.value)

#     # Unsuccessful approval
#     # Due to reviewer being same as trainee
#     reviewer = crud.get_reviewer_by_id(db=db, reviewer_id=2)
#     reviewer_username = crud.get_user_by_id(db=db, user_id=reviewer.user_id).username
#     with pytest.raises(ValueError) as exc:
#         crud.approve_assessment(
#             db=db,
#             trainee=trainee,
#             assessment=assessment,
#             reviewer=reviewer,
#             reviewer_username=reviewer_username,
#         )
#     assert "Reviewer cannot be the same as the trainee." in str(exc.value)

#     # Unsuccessful approval
#     # Due to reviewer being different from the assessment tracker record
#     # Update logs to pass checks
#     assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
#         db=db, entry_id=6
#     )
#     crud.update_assessment_log(
#         db=db,
#         entry_id=assessment_tracker_entry.id,
#         latest_commit=assessment_tracker_entry.latest_commit,
#         update_logs={
#             "checks_passed": True,
#             "commit": assessment_tracker_entry.latest_commit,
#         },
#     )
#     reviewer = crud.get_reviewer_by_id(db=db, reviewer_id=5)
#     reviewer_username = crud.get_user_by_id(db=db, user_id=reviewer.user_id).username
#     with pytest.raises(ValueError) as exc:
#         crud.approve_assessment(
#             db=db,
#             trainee=trainee,
#             assessment=assessment,
#             reviewer=reviewer,
#             reviewer_username=reviewer_username,
#         )
#     assert (
#         "Reviewer is not the same as the reviewer assigned to the assessment."
#         in str(exc.value)
#     )


# def test_sync_badges(db: Session):
#     """Test sync badges."""
#     # Sync badges
#     crud.sync_badges(db=db, settings=settings)


# def test_add_assertion(db: Session):
#     """Test add assertion."""

#     # Get assertion from badgr
#     bt = utils.get_bearer_token(config=settings)
#     resp = utils.get_assertion(
#         assessment_name="Test", user_email="nicole_cayer3@gmail.com",
#         bearer_token=bt, config=settings
#     )
#     assert resp.status_code == 200
#     assert resp.json()["status"] == {'description': 'ok', 'success': True}

#     assertion = resp.json()["result"][0]

#     # Change entity ID
#     assertion["entityId"] = "ABC"

#     # Add assertion
#     res = crud.add_assertion(
#         db=db, settings=settings, assertion=assertion, entry_id=6
#     )
#     assert res


#     # Fail on second add
#     with pytest.raises(IntegrityError) as exc:
#         crud.add_assertion(
#             db=db, settings=settings, assertion=assertion, entry_id=6
#         )


#     # Fail on invalid assertion
#     assertion2 = copy.deepcopy(assertion)
#     # Drop the entity ID
#     assertion2.pop("entityId")
#     with pytest.raises(KeyError) as exc:
#         crud.add_assertion(
#             db=db, settings=settings, assertion=assertion2, entry_id=6
#         )

#     # Fail on invalid assertion due to missing badgeclass
#     assertion2 = copy.deepcopy(assertion)
#     # Drop the badgeclass
#     assertion2.pop("badgeclass")
#     with pytest.raises(KeyError) as exc:
#         crud.add_assertion(
#             db=db, settings=settings, assertion=assertion2, entry_id=6
#         )

#     # Add a second assertion where the expires field is set
#     # in %Y-%m-%dT%H:%M:%SZ format
#     assertion2 = copy.deepcopy(assertion)
#     assertion2["expires"] = "2020-01-01T00:00:00Z"
#     assertion2["entityId"] = "ABCDEF"
#     res = crud.add_assertion(
#         db=db, settings=settings, assertion=assertion2, entry_id=1
#     )
#     assert res

#     # Add a second assertion where the recipient identity is set to 'url'
#     # instead of email
#     assertion2 = copy.deepcopy(assertion)
#     assertion2["recipient"]["type"] = "url"
#     # Drop recipient salt
#     assertion2["recipient"].pop("salt")
#     # Drop evidence
#     assertion2['evidence'] = []
#     assertion2["entityId"] = "ABCDEFGHI"
#     res = crud.add_assertion(
#         db=db, settings=settings, assertion=assertion2, entry_id=2
#     )
#     assert res


# def test_update_assessment_log(db: Session):

#     # Get data from database & fake commit
#     assessment_tracker_entry = crud.get_assessment_tracker_entry(
#         db=db, user_id=1, assessment_id=2
#     )
#     commit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

#     # Update assessment log
#     test_log = {"Test update log": True}
#     update_logs = crud.update_assessment_log(
#         db=db,
#         entry_id=assessment_tracker_entry.id,
#         latest_commit=commit,
#         update_logs=copy.deepcopy(test_log),
#     )
#     assert update_logs
#     # Verify that the log is updated
#     assessment_tracker_entry = crud.get_assessment_tracker_entry(
#         db=db, user_id=1, assessment_id=2
#     )
#     assert assessment_tracker_entry.assessment_id == 2
#     assert assessment_tracker_entry.user_id == 1
#     assert assessment_tracker_entry.latest_commit == commit
#     logs = list(assessment_tracker_entry.log)
#     assert logs[-1]["Test update log"]

#     # Unsuccessful update
#     # Due to incorrect assessment tracker ID
#     with pytest.raises(ValueError) as exc:
#         crud.update_assessment_log(
#             db=db,
#             entry_id=0,
#             latest_commit=commit,
#             update_logs=copy.deepcopy(test_log),
#         )
#     assert "Assessment tracker entry unavailable." in str(exc.value)
