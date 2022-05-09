from datetime import datetime
from sqlalchemy.orm import Session
import random
from app import models, schemas, utils


# Reproducibility for randomly selecting reviewers
random.seed(42)


def get_user_by_username(db: Session, username: str):
    """
    Return the user's entry.

    :param db: Generator for Session of database
    :param username: imputs github username

    :returns: Entry in Users table.

    :errors: ValueError if user does not exist.
    """
    user = (
        db.query(models.Users).filter(models.Users.github_username == username).first()
    )
    if user is None:
        raise ValueError("User name does not exist")
    return user


def get_user_by_id(db: Session, user_id: int):
    """
    Return the user's details.
    """
    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if user is None:
        raise ValueError("User ID does not exist")
    return user


def get_reviewer_by_username(db: Session, username: str):
    """
    Return the reviewer's id from username.

    :param db: Generator for Session of database
    :param username: inputs reviewer's username

    :returns: reviewer id

    :errors: ValueError if reviewer does not exist.
    """
    reviewer_user_id = get_user_by_username(db=db, username=username).user_id
    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.user_id == reviewer_user_id)
        .first()
    )
    if reviewer is None:
        raise ValueError("Reviewer does not exist")

    return reviewer


def get_reviewer_by_id(db: Session, reviewer_id: int):
    """
    Return the reviewer's details.
    """
    reviewer = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.reviewer_id == reviewer_id)
        .first()
    )
    if reviewer is None:
        raise ValueError("Reviewer does not exist")
    return reviewer


def get_assessment_by_name(db: Session, assessment_name: str):
    """
    Return the assessment's id.

    :param db: Generator for Session of database
    :param assessment_name: inputs assessment name

    :returns: assessment id

    :errors: ValueError if assessment does not exist.
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
    Return the assessment's details.
    """
    assessment = (
        db.query(models.Assessments)
        .filter(models.Assessments.assessment_id == assessment_id)
        .first()
    )
    if assessment is None:
        raise ValueError("Assessment ID does not exist")
    return assessment


def get_assessment_tracker_entry(db: Session, user_id: int, assessment_id: int):
    """
    Return the user's assessment tracker entry.

    :param db: Generator for Session of database
    :param user_id: inputs user's id
    :param assessment_id: inputs assessment id

    :returns: Assessment_tracker object containing the details of the entry made.

    :errors: ValueError if assessment tracker entry does not exist.
    """
    assessment_tracker = (
        db.query(models.AssessmentTracker)
        .filter(
            models.AssessmentTracker.user_id == user_id,
            models.AssessmentTracker.assessment_id == assessment_id,
        )
        .first()
    )
    if assessment_tracker is None:
        raise ValueError("Assessment tracker entry unavailable.")

    return assessment_tracker


def get_assessment_tracker_entry_by_id(db: Session, assessment_tracker_entry_id: int):
    """
    Return the assessment tracker entry.

    :param db: Generator for Session of database
    :param assessment_tracker_entry_id: inputs assessment tracker entry id

    :returns: Assessment_tracker object containing the details of the entry made.

    :errors: ValueError if assessment tracker entry does not exist.

    """
    assessment_tracker = (
        db.query(models.AssessmentTracker)
        .filter(models.AssessmentTracker.entry_id == assessment_tracker_entry_id)
        .first()
    )
    if assessment_tracker is None:
        raise ValueError("Assessment tracker entry unavailable.")

    return assessment_tracker


def get_assessment_tracker_entry_by_commit(db: Session, commit: str):
    """
    Return the assessment tracker entry by last commit.
    This DOES NOT work as part of update commands, as these may
    contain a new commit which is not yet registered in the tracker.
    It should really only be applied for the /check and /approve endpoints.
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
    Invoked by /api/init_assessment endpoint.
    Initiates/adds a fresh entry in assessment_tracker table.

    :param db: Generator for Session of database
    :param assessment_tracker: inputs user's github username, assessment name and latest commit.

    :returns: Assessment_tracker object containing the details of the entry made.

    :errors: ValueError if assessment tracker entry has already been initiated.
    """
    # Get assessment id
    assessment_id = get_assessment_by_name(
        db=db, assessment_name=init_request.assessment_name
    ).assessment_id

    # Check if assessment tracker entry exists and if not, create one
    try:
        get_assessment_tracker_entry(
            db=db, user_id=user_id, assessment_id=assessment_id
        )
        raise ValueError("Assessment tracker entry already exists.")
    except ValueError as e:
        # Raise the error if it's not about a missing entry
        if str(e) != "Assessment tracker entry unavailable.":
            raise e

        # Create a new entry if it doesn't exist
        db_obj = models.AssessmentTracker(
            assessment_id=assessment_id,
            user_id=user_id,
            latest_commit=init_request.latest_commit,
            last_updated=datetime.utcnow(),
            status="Initiated",
            log=[
                {
                    "Status": "Initiated",
                    "Updated": str(datetime.utcnow()),
                    "Commit": init_request.latest_commit,
                }
            ],
        )
        db.add(db_obj)
        db.commit()

        return True


def select_reviewer(db: Session, assessment_tracker_entry: models.AssessmentTracker):
    """
    Invoked by /api/init_review endpoint
    Used to get the reviewer's github username

    This currently assumes we will be using the information about the
    skill assessment in order to select a reviewer
    """
    user = get_user_by_id(db=db, user_id=assessment_tracker_entry.user_id)
    try:
        invalid_rev = get_reviewer_by_username(
            db=db,
            username=user.github_username,
        ).reviewer_id
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
    random_reviewer_id = valid_reviewers[random.randint(0, len(valid_reviewers) - 1)][0]

    # Return the reviewer's db entry
    random_reviewer = get_reviewer_by_id(db=db, reviewer_id=random_reviewer_id)
    return random_reviewer


def assign_reviewer(
    db: Session, assessment_tracker_entry: models.AssessmentTracker, reviewer_info: dict
):
    """
    Invoked by /api/init_review endpoint
    Used to assign a reviewer to an assessment tracker entry

    :param db: Generator for Session of database
    :param assessment_tracker_entry: inputs assessment tracker entry id
    :param reviewer_info: dict containing reviewer's github username and id
    """
    # Update the assessment tracker entry
    assessment_tracker_entry.reviewer_id = reviewer_info["reviewer_id"]
    assessment_tracker_entry.status = "Under review"
    assessment_tracker_entry.last_updated = datetime.utcnow()
    db.add(assessment_tracker_entry)
    db.commit()

    # Update the assessment tracker entry log
    update_assessment_log(
        db=db,
        assessment_tracker_entry_id=assessment_tracker_entry.entry_id,
        latest_commit=assessment_tracker_entry.latest_commit,
        update_logs=reviewer_info,
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
    Invoked by /api/approve endpoint.
    Changes the status of the assessment_tracker data, updates the log accordingly

    :param db: Generator for Session of database
    :param trainee: Entry from user table for trainee
    :param reviewer: Entry from reviewer table for reviewer
    :param assessment: Entry from assessment table for assessment

    :returns: boolean True if the assessment is approved and badge is awarded.
    """
    # Get user ids and confirm they are different
    if reviewer.user_id == trainee.user_id:
        raise ValueError("Reviewer cannot be the same as the trainee.")

    # Verify checks passing on latest commit
    assessment_tracker_entry = get_assessment_tracker_entry(
        db=db, user_id=trainee.user_id, assessment_id=assessment.assessment_id
    )
    if assessment_tracker_entry.reviewer_id is None:
        raise ValueError("No reviewer is assigned to the assessment.")
    if assessment_tracker_entry.status != "Under review":
        raise ValueError("Assessment is not under review.")
    if not utils.verify_check(assessment_tracker_entry=assessment_tracker_entry):
        raise ValueError("Last commit checks failed.")

    # Get the reviewer, based on the assessment_tracker entry
    reviewer_real = get_reviewer_by_id(
        db=db, reviewer_id=assessment_tracker_entry.reviewer_id
    )
    reviewer_real_user = get_user_by_id(db=db, user_id=reviewer_real.user_id)
    # Verify the approval request is from the reviewer
    if reviewer_real_user.github_username != reviewer_username:
        raise ValueError(
            "Reviewer is not the same as the reviewer assigned to the assessment."
        )

    # Get assessment id and latest commit
    latest_commit = assessment_tracker_entry.latest_commit

    # Approve the assessment and update the log / status
    assessment_tracker_entry.status = "Approved"
    assessment_tracker_entry.last_updated = datetime.utcnow()
    log = {
        "Updated": str(datetime.utcnow()),
        "Status": "Approved",
        "Commit": latest_commit,
        "Reviewer": reviewer.reviewer_id,
    }
    logs = list(assessment_tracker_entry.log)
    logs.append(log)
    assessment_tracker_entry.log = logs
    db.add(assessment_tracker_entry)
    db.commit()

    return True


def update_assessment_log(
    db: Session, assessment_tracker_entry_id: int, latest_commit: str, update_logs: dict
):
    """
    It updates the logs of the entry in assessmnet_tracker table

    :param db: Generator for Session of database
    :param asses_track_info: user github username, assessment name, latest commit
    :param update_logs: logs to be added

    :returns: assessment_tracker object with the updated entry
    """
    # Get the assessment tracker entry
    assessment_tracker_entry = get_assessment_tracker_entry_by_id(
        db=db, assessment_tracker_entry_id=assessment_tracker_entry_id
    )

    # Update the logs
    assessment_tracker_entry.last_updated = datetime.utcnow()
    assessment_tracker_entry.latest_commit = latest_commit
    logs = list(assessment_tracker_entry.log)
    logs.append(update_logs)
    assessment_tracker_entry.log = logs

    # Commit the changes
    db.add(assessment_tracker_entry)
    db.commit()

    return True
