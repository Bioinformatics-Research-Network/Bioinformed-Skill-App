from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app import schemas


def get_user_by_username(db: Session, username: str):
    """
    Return the user's entry.
    
    :param db: Generator for Session of database
    :param username: imputs github username

    :returns: Entry in Users table.

    :errors: ValueError if user does not exist.
    """
    user = (
        db.query(models.Users)
        .filter(models.Users.github_username == username)
        .first()
    )
    if user is None:
        raise ValueError("User name does not exist")
    return user


def get_user_by_id(db: Session, user_id: int):
    """
    Return the user's details.
    """
    user = (
        db.query(models.Users)
        .filter(models.Users.user_id == user_id)
        .first()
    )
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
        .with_entities(models.Reviewers.reviewer_id)
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
        .with_entities(models.Assessments.assessment_id)
        .first()
    )
    if assessment is None:
        raise ValueError("Assessment does not exist")

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
        raise ValueError("Assessment entry unavailable.")
    
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
    Return the assessment tracker entry by commit.
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
    assessment_tracker: schemas.assessment_tracker_init,
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
        db=db, assessment_name=assessment_tracker.assessment_name
    ).assessment_id

    # Check if assessment exists
    if assessment_id is None:
        raise ValueError("Assessment name is invalid.")

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
            latest_commit=assessment_tracker.latest_commit,
            last_updated=datetime.utcnow(),
            status="Initiated",
            log=[
                {
                    "Status": "Initiated",
                    "Updated": str(datetime.utcnow()),
                    "Commit": assessment_tracker.latest_commit,
                }
            ],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj


def verify_check(db: Session, assessment_tracker_entry_id: int):
    """
    Verifies that the commit is passing the checks.

    :param db: Generator for Session of database
    :param user: github username
    :param assessment_name: assessment name

    :returns: boolean True if the commit is passing the checks.

    :errors: ValueError if logs are not available or if the commit has not been checked.
    """
    # Get assessment tracker entry
    assessment_id = get_assessment_by_name(db=db, assessment_name=assessment_name).assessment_id
    user_id = get_user_by_username(db=db, username=user).user_id
    assessment_tracker = get_assessment_tracker_entry(
        db=db, user_id=user_id, assessment_id=assessment_id
    )
    
    # Get the log 
    log = assessment_tracker.log
    if log is None:
        raise ValueError("No logs found.")

    # Get latest commit    
    last_log_by_commit = [
        lg for lg in log if lg.get("Commit", "NA") == assessment_tracker.latest_commit
    ]
    if last_log_by_commit == []:
        raise ValueError("No logs found for last commit.")

    # Get the logs where checks were run
    commit_log_checks = [
        lg for lg in last_log_by_commit if "Checks_passed" in lg.keys()
    ]
    if commit_log_checks == []:
        raise ValueError("Check results not available for latest commit.")
    last_log = last_log_by_commit[-1]

    # Return checks results
    return last_log['Checks_passed']


def approve_assessment(
    db: Session,
    trainee_username: int,
    reviewer_username: int,
    assessment_name: str,
):
    """
    Invoked by /api/approve_assessment endpoint.
    Changes the status of the assessment_tracker data, updates the log accordingly

    :param db: Generator for Session of database
    :param trainee_username: github username for trainee.
    :param reviewer_username: github username for reviewer.
    :param assessment_name: assessment name of the related assessment

    :returns: assessment_tracker object with the updated entry
    """
    # Get user ids and confirm they are different
    trainee_userid = get_user_by_username(db=db, username=trainee_username).user_id
    reviewer_userid = get_reviewer_by_username(db=db, username=reviewer_username).user_id
    if trainee_userid == reviewer_userid:
        raise ValueError("Trainee and reviewer cannot be the same.")

    # Verify checks passing on latest commit
    if not verify_check(db=db, user=trainee_username, assessment_name=assessment_name):
        raise ValueError("Last commit checks failed.")
    
    # Get assessment id and latest commit
    assessment_id = get_assessment_id(db=db, assessment_name=assessment_name)
    assessment_entry = get_assessment_tracker_entry(
        db=db, user_id=trainee_userid, assessment_id=assessment_id
    )
    latest_commit = assessment_entry.latest_commit
    
    # Approve the assessment
    assessment_entry.status = "Approved"
    assessment_entry.last_updated = datetime.utcnow()
    log = {
        "Updated": str(datetime.utcnow()),
        "Status": "Approved", 
        "Commit": latest_commit,
        "Reviewer": reviewer_id,
    }
    logs = list(assessment_entry.log)
    logs.append(log)
    assessment_entry.log = logs

    db.add(assessment_entry)
    db.commit()
    db.refresh(assessment_entry)

    return True


def update_assessment_log(
    db: Session, assessment_tracker_id, latest_commit, update_logs: dict
):
    """
    It updates the logs of the entry in assessmnet_tracker table

    :param db: Generator for Session of database
    :param asses_track_info: user github username, assessment name, latest commit
    :param update_logs: logs to be added

    :returns: assessment_tracker object with the updated entry
    """
    assess_track_entry = (
        db.query(models.AssessmentTracker)
        .filter(
            models.AssessmentTracker.entry_id == assessment_tracker_id
        )
        .first()
    )
    if assess_track_entry is None:
        raise ValueError("No assessment tracker entry found.")

    # Update the logs
    assess_track_entry.last_updated = datetime.utcnow()
    assess_track_entry.latest_commit = latest_commit
    logs = list(assess_track_entry.log)
    logs.append(update_logs)
    assess_track_entry.log = logs

    # Commit the changes
    db.add(assess_track_entry)
    db.commit()
    db.refresh(assess_track_entry)

    return assess_track_entry



