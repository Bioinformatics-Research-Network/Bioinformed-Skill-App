from datetime import datetime
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas


def verify_member(db: Session, username: str):
    """
    Verifies if the member exists in the User table of the database.

    :param db: Generator for Session of database
    :param username: imputs github username

    :returns: User id and first name of the member.
              None if the member doesn;t exist in the db.
    """
    return (
        db.query(models.Users)
        .filter(models.Users.github_username == username)
        .with_entities(models.Users.user_id, models.Users.first_name)
        .first()
    )


def verify_reviewer(db: Session, reviewer_username: str):
    """
    Verifies if the reviewer exists in the User table of the database.
    If member is verified, crosschecks if it is a reviewer from the database.

    :param db: Generator for Session of database
    :param reviewer_username: imputs github username of reviewer

    :returns: reviewer id of the reviewer.
              None if the reviewer doesn't exist in the db.
    """

    reviewer = verify_member(db=db, username=reviewer_username)

    if reviewer is None:
        return None

    reviewer_id = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.user_id == reviewer.user_id)
        .with_entities(models.Reviewers.reviewer_id)
        .first()
    )

    return reviewer_id


def assessment_id_tracker(db: Session, assessment_name: str):
    """
    It checks if the assessment name is valid, if yes outputs assessment id.

    :param db: Generator for Session of database
    :param assessment_name: inputs assessment name

    :returns: assessment id, None if assessment name is invalid
    """
    assessment_id = (
        db.query(models.Assessments)
        .filter(models.Assessments.name == assessment_name)
        .with_entities(models.Assessments.assessment_id)
        .first()
    )
    if assessment_id is None:
        return None

    return assessment_id.assessment_id


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
    """

    assessment_id = assessment_id_tracker(
        db=db, assessment_name=assessment_tracker.assessment_name
    )

    if assessment_id is None:
        raise ValueError("Assessment name is invalid")

    check_commit = (
        db.query(models.Assessment_Tracker)
        .filter(
            models.Assessment_Tracker.latest_commit == assessment_tracker.latest_commit
        )
        .one_or_none()
    )
    if check_commit is not None:
        return None

    assessment_init_check = (
        db.query(models.Assessment_Tracker)
        .filter(
            models.Assessment_Tracker.user_id == user_id,
            models.Assessment_Tracker.assessment_id == assessment_id,
        )
        .one_or_none()
    )

    if assessment_init_check is not None:
        return None

    db_obj = models.Assessment_Tracker(
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


def approve_assessment_crud(
    db: Session,
    user_id: int,
    # reviewer_id: int, use this to check if the reviewer is correct for the given assessment tracker
    # will be used when reviewers are assigned and updated in assessment_tracker table
    assessment_name: str,
):
    """
    Invoked by /api/approve_assessment endpoint.
    Changes the status of the assessment_tracker data, updates the log accordingly

    :param db: Generator for Session of database
    :param user_id: unique user id for each member.
    :param assessment_name: assessment name of the related assessment

    :returns: assessment_tracker object with the updated entry
    """
    assessment_id = assessment_id_tracker(db=db, assessment_name=assessment_name)
    if assessment_id is None:
        return None

    approve_assessment_data = (
        db.query(models.Assessment_Tracker)
        .filter(
            models.Assessment_Tracker.user_id == user_id,
            models.Assessment_Tracker.assessment_id == assessment_id,
        )
        .first()
    )

    if approve_assessment_data is None:
        return None

    approve_assessment_data.status = "Approved"
    approve_assessment_data.last_updated = datetime.utcnow()
    log = {"Updated": str(datetime.utcnow()), "Status": "Approved"}
    logs = list(approve_assessment_data.log)
    logs.append(log)
    approve_assessment_data.log = logs

    db.add(approve_assessment_data)
    db.commit()
    db.refresh(approve_assessment_data)

    return approve_assessment_data


def update_assessment_log(
    db: Session, asses_track_info: schemas.check_update, update_logs: dict
):
    """
    It updates the logs of the entry in assessmnet_tracker table

    :param db: Generator for Session of database
    :param asses_track_info: user github username, assessment name, latest commit
    :param update_logs: logs to be added

    :returns: assessment_tracker object with the updated entry
    """
    assessment_id = assessment_id_tracker(
        db=db, assessment_name=asses_track_info.assessment_name
    )

    user = verify_member(db=db, username=asses_track_info.github_username)
    if user is None or assessment_id is None:
        return None
    # first read the data which is to be updated

    assess_track_data = (
        db.query(models.Assessment_Tracker)
        .filter(
            models.Assessment_Tracker.user_id == user.user_id,
            models.Assessment_Tracker.assessment_id == assessment_id,
        )
        .first()
    )
    if assess_track_data is None:
        return None

    assess_track_data.last_updated = datetime.utcnow()
    assess_track_data.latest_commit = asses_track_info.commit
    logs = list(assess_track_data.log)
    logs.append(update_logs)
    assess_track_data.log = logs

    db.add(assess_track_data)
    db.commit()
    db.refresh(assess_track_data)

    return assess_track_data


def verify_check(db: Session, user: str, commit: str):
    """
    Verifies that the commit is passing the checks.

    :param db: Generator for Session of database
    :param username: imputs github username

    :returns: User id and first name of the member.
              None if the member doesn;t exist in the db.
    """
    user_id = (
        db.query(models.Users)
        .filter(models.Users.github_username == user)
        .first()
    )
    if user_id is None:
        raise ValueError("User does not exist")
    
    last_commit = (
        db.query(models.Assessment_Tracker)
        .filter(
            models.Assessment_Tracker.latest_commit == commit,
        )
        .first()
    )
    if last_commit is None:
        raise ValueError("Commit does not exist")
    
    log = last_commit.log
    if log is None:
        raise ValueError("Log does not exist")

    # [ log_dict['Checks_passed'] for log_dict in log ]
       
    print(log)

    return log

