from datetime import datetime
import random
from sqlalchemy.orm import Session
from app import schemas, crud, models

random.seed(42)

def run_gha(check: schemas.check_update):
    """
    Invoked by /api/init_check endpoint
    Used to run the GitHub Actions checks on the commit reuired

    :param check: user's github username, assessment name and latest commit

    :returns: logs from the GHA
    """

    logs = schemas.update_log(
        log={
            "Updated": str(datetime.utcnow()),
            "Checks_passed": True,
            "Commit": check.commit,
        }
    )
    return logs


def get_reviewer(
    db: Session, 
    assessment_tracker_entry_id: int
):
    """
    Invoked by /api/init_review endpoint
    Used to get the reviewer's github username

    This currently assumes we will be using the information about the 
    skill assessment in order to select a reviewer
    """
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(
        db=db, assessment_tracker_entry_id=assessment_tracker_entry_id
    )
    user = crud.get_user_by_id(
        db=db, user_id=assessment_tracker_entry.user_id
    )
    assessment = crud.get_assessment_by_id(
        db=db, assessment_id=assessment_tracker_entry.assessment_id
    )

    try:
        invalid_rev = crud.get_reviewer_by_username(
            db=db,
            username=user.github_username,
        )  # trainee is a reviewer
    except ValueError as e:
        if str(e) != "Reviewer does not exist":
            raise ValueError(str(e))  # Raise error if not expected
        else:
            invalid_rev = 0  # trainee is not a reviewer

    # Get all reviewers
    valid_reviewers = (
        db.query(models.Reviewers)
        .filter(
            models.Reviewers.reviewer_id != invalid_rev,
            # Uncomment to filter by assessments the reviewer can do
            # assessment.assessment_id in models.Reviewers.assessment_reviewing_info,
        )
        .with_entities(models.Reviewers.reviewer_id)
        .all()
    )

    # Get a random reviewer from the list of valid reviewers
    # Will be replaced with Slack integration
    random_reviewer = valid_reviewers[
        random.randint(0, len(valid_reviewers) - 1)
    ]

    return random_reviewer
