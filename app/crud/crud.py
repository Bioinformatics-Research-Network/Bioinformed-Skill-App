from datetime import datetime
from sqlalchemy.orm import Session
import random
import requests
import copy
from app import models, schemas, utils
from app.config import Settings
from app.models.models import Badges


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
    user = db.query(models.Users).filter(models.Users.username == username).first()
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
        db.query(models.Reviewers).filter(models.Reviewers.user_id == user_id).first()
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
        db.query(models.Reviewers).filter(models.Reviewers.id == reviewer_id).first()
    )
    if reviewer is None:
        raise ValueError("Reviewer does not exist")

    return reviewer


# Get reviewer by user id
def get_reviewer_by_user_id(db: Session, user_id: int) -> models.Reviewers:
    """
    To get reviewer by user id.
    """
    reviewer = db.query(models.Reviewers).filter_by(user_id=user_id).first()
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


def create_assessment_tracker_entry(
    db: Session,
    user_id: int,
    assessment_id: int,
    commit: str,
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

        # Create a new entry if it doesn't exist yet
        db_obj = models.AssessmentTracker(
            user_id=user_id,
            assessment_id=assessment_id,
            last_updated=datetime.utcnow(),
            status="Pre-assessment",
            latest_commit=commit,
            log=[
                {
                    "status": "Pre-assessment",
                    "timestamp": str(datetime.utcnow()),
                    "commit": None
                }
            ],
        )
        db.add(db_obj)
        db.commit()

        return True


def update_assessment_tracker_entry(
    db: Session,
    user_id: int,
    assessment_id: int,
    status: str,
    commit: str,
    github_url: str,
):
    """
    Update the assessment tracker entry

    :param db: Generator for Session of database
    :param user_id: user id
    :param assessment_id: assessment id
    :param status: status
    :param commit: commit
    :param repo_url: repo url
    :param repo_branch: repo branch

    :returns: True
    """
    # Get the assessment tracker entry
    assessment_tracker = get_assessment_tracker_entry(
        db=db, assessment_id=assessment_id, user_id=user_id
    )
    
    try:
        # Update the entry
        assessment_tracker.status = status
        assessment_tracker.latest_commit = commit
        assessment_tracker.repo_owner = github_url.split("/")[3]
        assessment_tracker.repo_name = github_url.split("/")[4]
        assessment_tracker.pr_number = 1
        assessment_tracker.last_updated = datetime.utcnow()
        # Add the new log entry
        assessment_tracker.log.append(
            {
                "status": status,
                "timestamp": str(datetime.utcnow()),
                "commit": commit
            }
        )
        db.commit()
        return True
    except Exception as e:
        print(e)
        db.rollback()
        raise e


def select_reviewer(db: Session, assessment_tracker_entry: models.AssessmentTracker):
    """
    Select a reviewer for the assessment tracker entry.

    :param db: Generator for Session of database
    :param assessment_tracker_entry: assessment tracker entry

    :returns: Reviewer info as an entry from the Reviewer's table in sqlalchemy query object format.

    :raises: Uncaught error if no reviewer is available (should not happen).
    """
    invalid_rev = (
        db.query(models.Reviewers)
        .filter(models.Reviewers.user_id == assessment_tracker_entry.user_id)
        .with_entities(models.Reviewers.id)
        .all()
    )
    invalid_rev = [i[0] for i in invalid_rev]

    # Get all reviewers
    valid_reviewers = (
        db.query(models.Reviewers)
        .filter(
            models.Reviewers.id.notin_(invalid_rev),
            # Uncomment to filter by assessments the reviewer can do
            # assessment.id in models.Reviewers.assessment_reviewing_info,
        )
        .with_entities(models.Reviewers.id)
        .all()
    )

    try:
        # Get a random reviewer from the list of valid reviewers
        # Will be replaced with Slack integration
        random_id = valid_reviewers[random.randint(0, len(valid_reviewers) - 1)][0]
    except Exception as e: # pragma: no cover
        raise ValueError("No reviewer available. Please contact the administrator.")

    try:
        random_reviewer = get_reviewer_by_id(db=db, reviewer_id=random_id)
        return random_reviewer
    except Exception as e:  # pragma: no cover
        raise Exception("Error selecting reviewer. Contact the administrators. Error string: " + str(e))


def assign_reviewer(
    db: Session, assessment_tracker_entry: models.AssessmentTracker, reviewer_info: dict
):
    """
    Assign a reviewer to the assessment tracker entry.

    :param db: Generator for Session of database
    :param assessment_tracker_entry: assessment tracker entry
    :param reviewer_info: reviewer info. Dict following the format:
        { "reviewer_id": int, "reviewer_username": str }

    :returns: True

    :raises: None (hopefully)
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
        entry_id=assessment_tracker_entry.id,
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


    # Verify checks passing on latest commit
    assessment_tracker_entry = get_assessment_tracker_entry(
        db=db, user_id=trainee.id, assessment_id=assessment.id
    )
    
    if not utils.verify_check(assessment_tracker_entry=assessment_tracker_entry):
        raise ValueError("Last commit checks failed.")

    # Verify that the reviewer is the same as the reviewer assigned in the assessment tracker entry
    if assessment.review_required == 1:
        # Get user ids and confirm they are different
        if reviewer.user_id == trainee.id:
            raise ValueError("Reviewer cannot be the same as the trainee.")
        if assessment_tracker_entry.reviewer_id is None:
            raise ValueError("No reviewer is assigned to the assessment.")
        if assessment_tracker_entry.status != "Under review":
            raise ValueError("Assessment is not under review.")

        # Get the reviewer, based on the assessment_tracker entry
        reviewer_real = get_reviewer_by_id(
            db=db, reviewer_id=assessment_tracker_entry.reviewer_id
        )
        reviewer_real_user = get_user_by_id(db=db, user_id=reviewer_real.user_id)
        # Verify the approval request is from the reviewer
        if reviewer_real_user.username != reviewer_username:
            raise ValueError(
                "Reviewer is not the same as the reviewer assigned to the assessment."
            )
        reviewer = reviewer.id
    else:
        reviewer = 'brnbot'

    # Get assessment id and latest commit
    latest_commit = assessment_tracker_entry.latest_commit

    # Approve the assessment and update the log / status
    assessment_tracker_entry.status = "Approved"
    assessment_tracker_entry.last_updated = datetime.utcnow()
    log = {
        "timestamp": str(datetime.utcnow()),
        "status": "Approved",
        "commit": latest_commit,
        "Reviewer": reviewer,
    }
    logs = list(assessment_tracker_entry.log)
    logs.append(log)
    assessment_tracker_entry.log = logs
    db.add(assessment_tracker_entry)
    db.commit()

    return True


# Write a function that syncs the badges table with the badgr API
def sync_badges(
    settings: Settings, db: Session
):
    # Get all badges from the badgr API
    bt = utils.get_bearer_token(settings)
    try:
        badges = utils.get_all_badges(bt, settings)
        badgelst = badges.json()['result']
    except Exception as e: # pragma: no cover
        print(str(e))
        raise e

    # Loop through all badges and add them to the badges table
    try:
        for badge in badgelst:
            print(badge['name'])

            # Check if the badge already exists in the database
            current_badge = db.query(models.Badges).filter_by(name=badge['name'])

            # Convert all the fields to strings using dict comprehension
            fields = {k: str(v) for k, v in badge.items()}

            # If field is date, convert to datetime
            # fields = {k: datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ") if k == 'createdAt' else v for k, v in fields.items()}

            # Loop through all the fields and attempt to convert to datetime
            for k, v in fields.items():
                try: # pragma: no cover
                    if type(v) == str:
                        fields[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError: 
                    # Try different format
                    try:
                        fields[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        pass

            if current_badge.first() is None:
                print("Badge does not exist in database")
                badge = models.Badges(**fields)
                db.add(badge)
                db.commit()
            else:
                print('Badge already exists -- updating')
                # Update the badge in the database
                current_badge.update(values=fields)
                db.commit()
    except Exception as e: # pragma: no cover
        print(str(e))
        # Rollback the changes to the database
        db.rollback()
        raise e


def add_assertion(
    db: Session,
    settings: Settings,
    entry_id: int,
    assertion: str,
):
    """
    Add an assertion to the Assertions table.

    :param db: Generator
    :param entry_id: Assessment tracker entry id
    :param assertion: Assertion to add
    """
    badge = db.query(models.Badges).filter(models.Badges.entityId == assertion['badgeclass']).first()
    # Get the badge name for the assertion
    if badge is None:
        print("Syncing badges")
        sync_badges(settings=settings, db=db)
        badge = db.query(models.Badges).filter_by(entityId=assertion['badgeclass']).first()
    try:
        badge_name = badge.name
    except Exception as e: # pragma: no cover
        print(str(e))
        raise e
    
    # Wrangle the assertion
    fields = utils.wrangle_assertion(
        assertion=assertion,
        badge_name=badge_name,
    )

    # Add in the assessment_tracker ID
    fields["assessment_tracker_id"] = entry_id

    # Add the assertion to the Assertions table if it doesn't exist, else update it
    try:
        print("Assertion does not exist. Adding...")
        assertobj = models.Assertions(**fields)
        db.add(assertobj)
        db.commit()
        return True
    except Exception as e:
        print(fields)
        print(str(e))
        db.rollback()
        raise e


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


# Function to delete user
def delete_user(db: Session, user_id: int, settings: dict) -> None:
    """
    To delete user.
    """
    # Get the user
    user = db.query(models.Users).filter_by(id=user_id).first()

    # Uncover all repositories for the user by querying the assessment tracker
    assessment_tracker = (
        db.query(models.AssessmentTracker)
        .filter_by(user_id=user.id)
        .all()
    )

    # For each assessment tracker entry send a delete request to the bot
    if assessment_tracker:
        for at in assessment_tracker:
            assessment = db.query(models.Assessments).filter_by(id=at.assessment_id).first()
            payload = {
                "name": assessment.name,
                "install_id": int(assessment.install_id),
                "repo_prefix": assessment.repo_prefix,
                "github_org": assessment.github_org,
                "username": user.username,
            }
            print(payload)
            print("Sending request to bot init")
            response = requests.post(
                url=f"{settings.GITHUB_BOT_URL}/delete", 
                json=payload
            )
            print("Bot responded")
            response.raise_for_status()

    try:
        # Check for foreign key constraints
        # Reviewer
        reviewer = db.query(models.Reviewers).filter_by(user_id=user.id).first()
        if reviewer:
            # Get the reviewer and delete it
            reviewer = get_reviewer_by_user_id(db, user.id)
            db.delete(reviewer)
            db.commit()
        # OAuth
        print(user.id)
        oauth = db.query(models.OAuth).filter_by(user_id=user.id).first()
        print("OAUTH")
        print(oauth.__dict__)
        if oauth:
            db.delete(oauth)
            db.commit()
        # AssessmentTracker
        if assessment_tracker:
            # Delete all the assessment tracker entries connected to the user
            for at in assessment_tracker:
                # Get connected assertions
                assertions = (
                    db.query(models.Assertions)
                    .filter_by(assessment_tracker_id=at.id)
                    .first()
                )
                # If there are assertions, delete them
                if assertions:
                    # Delete assertions
                    db.delete(assertions)
                    db.commit()
                # Delete assessment tracker entry
                db.delete(at)
                db.commit()

        # Delete user
        db.delete(user)
        db.commit()
    except ValueError as e:
        print(str(e))
        db.rollback()
        print("rollback")
        raise e
    except Exception as e:  # pragma: no cover
        print(str(e))
        db.rollback()
        print("rollback")
        raise e

