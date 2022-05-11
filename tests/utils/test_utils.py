from sqlalchemy.orm import Session
from app import utils, crud, schemas
import pytest


# app.utils.runGHA
def test_run_gha(db: Session):
    log = utils.run_gha(commit="123456789")

    assert type(log["timestamp"]) == str
    assert log["checks_passed"] is True
    assert type(log["commit"]) == str


def test_verify_check(db: Session):
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, assessment_tracker_entry_id=1
    )
    # Fail due to missing checks
    with pytest.raises(ValueError) as exc:
        utils.verify_check(
            assessment_tracker_entry=assessment_tracker_entry,
        )
    assert "Check results not available for latest commit." in str(exc.value)

    ## Fail due to missing logs
    assessment_tracker_entry.log = None
    with pytest.raises(ValueError) as exc:
        utils.verify_check(
            assessment_tracker_entry=assessment_tracker_entry,
        )
    assert "No logs found." in str(exc.value)

    ## Fail due to missing log for last commit
    assessment_tracker_entry.log = [{"commit": "123456789"}]
    with pytest.raises(ValueError) as exc:
        utils.verify_check(
            assessment_tracker_entry=assessment_tracker_entry,
        )
    assert "No logs found for latest commit." in str(exc.value)

    # Checks passed
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, assessment_tracker_entry_id=1
    )
    crud.update_assessment_log(
        db=db,
        assessment_tracker_entry_id=assessment_tracker_entry.entry_id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": True,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, assessment_tracker_entry_id=1
    )
    assert utils.verify_check(
        assessment_tracker_entry=assessment_tracker_entry,
    )

    # Checks failed
    crud.update_assessment_log(
        db=db,
        assessment_tracker_entry_id=assessment_tracker_entry.entry_id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs={
            "checks_passed": False,
            "commit": assessment_tracker_entry.latest_commit,
        },
    )
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, assessment_tracker_entry_id=1
    )
    assert not utils.verify_check(
        assessment_tracker_entry=assessment_tracker_entry,
    )
