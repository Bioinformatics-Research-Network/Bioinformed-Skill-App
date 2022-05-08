from sqlalchemy.orm import Session
from app import utils, crud


# app.utils.runGHA
def test_runGHA(db: Session):
    request_json = schemas.check_update(
        github_username="test",
        assessment_name="test",
        commit="test",
    )
    log = utils.runGHA(
        check=request_json
    )  # logs = {"Updated": str(datetime.utcnow()), "Checks_passed": True, "Commit": commit}

    assert type(log.log["Updated"]) == str
    assert log.log["Checks_passed"] is True
    assert type(log.log["Commit"]) == str


def test_get_reviewer(db: Session):
    assessment_tracker_entry_id = 1

    user_id = crud.get_assessment_tracker_entry_by_id(
        db=db, assessment_tracker_entry_id=assessment_tracker_entry_id
    ).user_id
    
    reviewer = utils.get_reviewer(
        db=db, assessment_tracker_entry_id=assessment_tracker_entry_id
    )

    assert reviewer.user_id != user_id
    


