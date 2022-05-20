from datetime import datetime
from sqlalchemy.orm import Session
import random
import copy
from app import models, schemas, utils


# Reproducibility for randomly selecting reviewers
random.seed(42)


def get_user_by_username(db: Session, username: str):
    """
    Return the user entry based on username.

    :param db: Generator for Session of database
    :param username: github username

    :returns: Entry in Users table as a sqlalchemy query object.

    :raises: ValueError if user does not exist.
    """
    user = (
        db.query(models.Users).filter(models.Users.username == username).first()
    )
    if user is None:
        raise ValueError("User name does not exist")
    return user


def get_user_by_id(db: Session, user_id: int):
    """
    Return the user entry based on user id.

    :param db: Generator for Session of database
    :param id: user id

    :returns: Entry in Users table as a sqlalchemy query object.

    :raises: ValueError if user does not exist.
    """
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user is None:
        raise ValueError("User ID does not exist")
    return user


def get_reviewer_by_username(db: Session, username: str):
    """
    Return the reviewer entry based on username.

    :param db: Generator for Session of database
    :param username: github username

    :returns: Entry in Reviewers table as a sqlalchemy query object.

    :raises: ValueError if reviewer does not exist.
    """
    user_id = get_user_by_username(db=db, username=username).id
    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.id == user_id)
        .first()
    )
    if reviewer is None:
        raise ValueError("Reviewer does not exist")

    return reviewer


def get_reviewer_by_id(db: Session, reviewer_id: int):
    """
    Return the reviewer entry based on reviewer id.

    :param db: Generator for Session of database
    :param id: reviewer id

    :returns: Entry in Reviewers table as a sqlalchemy query object.

    :raises: ValueError if reviewer does not exist.
    """
    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.id == reviewer_id)
        .first()
    )
    if reviewer is None:
        raise ValueError("Reviewer does not exist")

    return reviewer


def get_assessment_by_name(db: Session, assessment_name: str):
    """
    Return the assessment entry based on assessment name.

    :param db: Generator for Session of database
    :param assessment_name: assessment name

    :returns: Entry in Assessments table as a sqlalchemy query object.

    :raises: ValueError if assessment does not exist.
    """
    assessment = (
        db.query(models.Assessments)
        .filter(models.Assessments.name == assessment_name)
        .first()
    )
    if assessment is None:
        raise ValueError("Assessment does not exist")

    return assessment


def get_assessment_by_id(db: Session, assessment_id: int):
    """
    Return the assessment entry based on assessment id.

    :param db: Generator for Session of database
    :param id: assessment id

    :returns: Entry in Assessments table as a sqlalchemy query object.

    :raises: ValueError if assessment does not exist.
    """
    assessment = (
        db.query(models.Assessments)
        .filter(models.Assessments.id == assessment_id)
        .first()
    )
    if assessment is None:
        raise ValueError("Assessment ID does not exist")
    return assessment


def get_assessment_tracker_entry(db: Session, user_id: int, assessment_id: int):
    """
    Return the assessment tracker entry.

    :param db: Generator for Session of database
    :param user_id: user id
    :param assessment_id: assessment id

    :returns: Assessment traker entry as an sqlalchemy query object.

    :raises: ValueError if assessment tracker entry does not exist.
    """
    assessment_tracker = (
        db.query(models.AssessmentTracker)
        .filter(models.AssessmentTracker.user_id == user_id)
        .filter(models.AssessmentTracker.assessment_id == assessment_id)
        .first()
    )
    if assessment_tracker is None:
        raise ValueError("Assessment tracker entry unavailable.")

    return assessment_tracker


def get_assessment_tracker_entry_by_id(db: Session, entry_id: int):
    """
    Return the assessment tracker entry by id.

    :param db: Generator for Session of database
    :param entry_id: assessment tracker entry id

    :returns: Assessment tracker entry as an sqlalchemy query object.

    :raises: ValueError if assessment tracker entry does not exist.
    """
    assessment_tracker = (
        db.query(models.AssessmentTracker)
        .filter(models.AssessmentTracker.id == entry_id)
        .first()
    )
    if assessment_tracker is None:
        raise ValueError("Assessment tracker entry unavailable.")

    return assessment_tracker


def get_assessment_tracker_entry_by_commit(db: Session, commit: str):
    """
    Return the assessment tracker entry by latest commit.

    :param db: Generator for Session of database
    :param commit: commit

    :returns: Assessment tracker entry as an sqlalchemy query object.

    :raises: ValueError if assessment tracker entry does not exist.
    """
    assessment_tracker = (
        db.query(models.AssessmentTracker)
        .filter(models.AssessmentTracker.latest_commit == commit)
        .first()
    )
    if assessment_tracker is None:
        raise ValueError("Assessment tracker entry unavailable.")

    return assessment_tracker


def init_assessment_tracker(
    db: Session,
    init_request: schemas.InitRequest,
    user_id: int,
):
    """
    Initialize the assessment tracker entry

    :param db: Generator for Session of database
    :param init_request: init request based on InitRequest schema

    :returns: True

    :raises: ValueError if:
        - Assessment does not exist
        - Assessment tracker entry already exists
        - User does not exist
    """
    # Get assessment id
    assessment_id = get_assessment_by_name(
        db=db, assessment_name=init_request.assessment_name
    ).id

    # Check if assessment tracker entry exists and if not, create one
    try:
        get_assessment_tracker_entry(
            db=db, assessment_id=assessment_id, user_id=user_id
        )
        raise ValueError("Assessment tracker entry already exists.")
    except ValueError as e:
        # Raise the error if it's not about a missing entry
        if str(e) != "Assessment tracker entry unavailable.":
            raise e

        # Create a new entry if it doesn't exist
        db_obj = models.AssessmentTracker(
            user_id=user_id,
            assessment_id=assessment_id,
            latest_commit=init_request.latest_commit,
            last_updated=datetime.utcnow(),
            status="Initiated",
            log=[
                {
                    "status": "Initiated",
                    "timestamp": str(datetime.utcnow()),
                    "commit": init_request.latest_commit,
                }
            ],
        )
        db.add(db_obj)
        db.commit()

        return True


def select_reviewer(db: Session, assessment_tracker_entry: models.AssessmentTracker):
    """
    Select a reviewer for the assessment tracker entry.

    :param db: Generator for Session of database
    :param assessment_tracker_entry: assessment tracker entry

    :returns: Reviewer info as an entry from the Reviewer's table in sqlalchemy query object format.

    :raises: Uncaught error if no reviewer is available (should not happen).
    """
    user = get_user_by_id(db=db, assessment_id=assessment_tracker_entry.id)
    try:
        invalid_rev = get_reviewer_by_username(
            db=db,
            username=user.username,
        ).id
    except ValueError as e:
        if str(e) != "Reviewer does not exist":  # pragma: no cover
            raise ValueError(str(e))  # Raise error if not expected
        else:
            invalid_rev = 0  # trainee is not a reviewer

    # Get all reviewers
    valid_reviewers = (
        db.query(models.Reviewers)
        .filter(
            models.Reviewers.id != invalid_rev,
            # Uncomment to filter by assessments the reviewer can do
            # assessment.id in models.Reviewers.assessment_reviewing_info,
        )
        .with_entities(models.Reviewers.id)
        .all()
    )

    try:
        # Get a random reviewer from the list of valid reviewers
        # Will be replaced with Slack integration
        random_id = valid_reviewers[
            random.randint(0, len(valid_reviewers) - 1)
        ][0]

        # Return the reviewer's db entry
        random_reviewer = get_reviewer_by_id(db=db, id=random_id)
        return random_reviewer
    except IndexError as e:  # pragma: no cover
        raise ValueError("No reviewer available. Contact the administrator.")


def assign_reviewer(
    db: Session, assessment_tracker_entry: models.AssessmentTracker, reviewer_info: dict
):
    """
    Assign a reviewer to the assessment tracker entry.

    :param db: Generator for Session of database
    :param assessment_tracker_entry: assessment tracker entry
    :param reviewer_info: reviewer info. Dict following the format:
        { "id": int, "reviewer_username": str }

    :returns: True

    :raises: None (hopefully)
    """
    # Update the assessment tracker entry
    assessment_tracker_entry.id = reviewer_info["id"]
    assessment_tracker_entry.status = "Under review"
    assessment_tracker_entry.last_updated = datetime.utcnow()
    db.add(assessment_tracker_entry)
    db.commit()

    # Update the assessment tracker entry log
    update_assessment_log(
        db=db,
        assessment_tracker_assessment_id=assessment_tracker_entry.id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs=copy.deepcopy(reviewer_info),
    )  # Update logs

    return True


def approve_assessment(
    db: Session,
    trainee: models.Users,
    reviewer: models.Reviewers,
    reviewer_username: str,
    assessment: models.Assessments,
):
    """
    Approve an assessment.

    :param db: Generator for Session of database
    :param trainee: trainee's db entry from the Users table in sqlalchemy query object format.
    :param reviewer: reviewer's db entry from the Reviewers table in sqlalchemy query object format.
    :param reviewer_username: reviewer's github username
    :param assessment: assessment's db entry from the Assessments table in sqlalchemy query object format.

    :returns: True

    :raises: ValueError if:
        - Reviewer is the same as the trainee
        - Assessment is already approved
        - Assessment is not under review
        - No reviewer is assigned
        - Last commit check failed
        - Assessment tracker entry does not exist
        - Reviewer is not the same as the reviewer assigned in the assessment tracker entry
    """
    # Get user ids and confirm they are different
    if reviewer.id == trainee.id:
        raise ValueError("Reviewer cannot be the same as the trainee.")

    # Verify checks passing on latest commit
    assessment_tracker_entry = get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )
    if assessment_tracker_entry.id is None:
        raise ValueError("No reviewer is assigned to the assessment.")
    if assessment_tracker_entry.status != "Under review":
        raise ValueError("Assessment is not under review.")
    if not utils.verify_check(assessment_tracker_entry=assessment_tracker_entry):
        raise ValueError("Last commit checks failed.")

    # Get the reviewer, based on the assessment_tracker entry
    reviewer_real = get_reviewer_by_id(
        db=db, assessment_id=assessment_tracker_entry.id
    )
    reviewer_real_user = get_user_by_id(db=db, reviewer_id=reviewer_real.id)
    # Verify the approval request is from the reviewer
    if reviewer_real_user.username != reviewer_username:
        raise ValueError(
            "Reviewer is not the same as the reviewer assigned to the assessment."
        )

    # Get assessment id and latest commit
    latest_commit = assessment_tracker_entry.latest_commit

    # Approve the assessment and update the log / status
    assessment_tracker_entry.status = "Approved"
    assessment_tracker_entry.last_updated = datetime.utcnow()
    log = {
        "timestamp": str(datetime.utcnow()),
        "status": "Approved",
        "commit": latest_commit,
        "Reviewer": reviewer.id,
    }
    logs = list(assessment_tracker_entry.log)
    logs.append(log)
    assessment_tracker_entry.log = logs
    db.add(assessment_tracker_entry)
    db.commit()

    return True


def update_assessment_log(
    db: Session, entry_id: int, latest_commit: str, update_logs: dict
):
    """
    Update the assessment tracker entry log.

    :param db: Generator for Session of database
    :param assessment_tracker_id: assessment tracker entry id
    :param latest_commit: latest commit
    :param update_logs: logs to update as a dict

    :returns: True

    :raises: ValueError if the assessment tracker entry does not exist
    """
    # Get the assessment tracker entry
    assessment_tracker_entry = get_assessment_tracker_entry_by_id(
        db=db, entry_id=entry_id
    )

    # Update the logs
    assessment_tracker_entry.last_updated = datetime.utcnow()
    assessment_tracker_entry.latest_commit = latest_commit
    logs = list(assessment_tracker_entry.log)
    update_logs["commit"] = latest_commit
    update_logs["timestamp"] = str(assessment_tracker_entry.last_updated)
    logs.append(update_logs)
    assessment_tracker_entry.log = logs

    # Commit the changes
    db.add(assessment_tracker_entry)
    db.commit()

    return True
