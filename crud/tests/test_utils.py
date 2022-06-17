from sqlalchemy.orm import Session
from app import utils, crud
import app.db.models as models
import pytest
import random
import string
import time

# Set random seed based on current time
random.seed(time.time())



def test_verify_check(db: Session):

    # get a user where username is brnbot
    trainee = db.query(models.Users).filter(models.Users.username == "brnbot").first()

    # Get assessment where name is Test
    assessment = db.query(models.Assessments).filter(models.Assessments.name == "Test").first()

    # Get assessment tracker entry
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )

    # If the assessment tracker entry exists, delete it and create a new one
    if assessment_tracker_entry:
        # Get any assertions tied to this entry
        assertions = db.query(models.Assertions).filter(
            models.Assertions.assessment_tracker_id == assessment_tracker_entry.id
        ).all()
        # Delete all assertions tied to this entry
        for assertion in assertions:
            db.delete(assertion)
        db.delete(assessment_tracker_entry)
        db.commit()

    # Create a new assessment tracker entry
    crud.create_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id,
        commit="".join(
            random.choices(string.ascii_uppercase + string.digits, k=20)
        )
    )
    # Get assessment tracker entry
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )

    # add log
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "test": "test"
        },
    )

    # Fail due to missing checks
    with pytest.raises(ValueError) as exc:
        utils.verify_check(
            assessment_tracker_entry=assessment_tracker_entry,
        )
    assert "Check results not available for latest commit." in str(exc.value)

    # Fail due to missing logs
    assessment_tracker_entry.log = None
    with pytest.raises(ValueError) as exc:
        utils.verify_check(
            assessment_tracker_entry=assessment_tracker_entry,
        )
    assert "No logs found." in str(exc.value)

    # Fail due to missing log for last commit
    assessment_tracker_entry.log = [{"commit": "123456789"}]
    with pytest.raises(ValueError) as exc:
        utils.verify_check(
            assessment_tracker_entry=assessment_tracker_entry,
        )
    assert "No logs found for latest commit." in str(exc.value)

    # Checks passed
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": True,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )
    assert utils.verify_check(
        assessment_tracker_entry=assessment_tracker_entry,
    )

    # Checks failed
    crud.update_assessment_log(
        db=db,
        entry_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": False,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    assessment_tracker_entry = crud.get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )
    assert not utils.verify_check(
        assessment_tracker_entry=assessment_tracker_entry,
    )
