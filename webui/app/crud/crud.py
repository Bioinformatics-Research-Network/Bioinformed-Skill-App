from app import models
from datetime import datetime
from sqlalchemy.orm import Session


# Create a function that retrieves all the assessments and their info
# from the database and returns them as a list of dictionaries.
def get_assessments(
    db: Session,
    user: models.Users,
    language: list = None,
    types: list = None,
    completed: bool = None,
) -> list:
    """
    To get all assessments from the database.
    """
    # Get the assessments where the languages and types are not None
    assessments = (
        db.query(models.Assessments)
        .filter(
            models.Assessments.languages.isnot(None),
            models.Assessments.types.isnot(None),
            models.Assessments.latest_release.isnot(None),
        )
        .all()
    )
    if language:
        assessments = [
            assessment
            for assessment in assessments
            if assessment.languages in language
        ]
    if types:
        assessments = [
            assessment
            for assessment in assessments
            if assessment.types in types
        ]
    if not completed == "true":
        # Get the user's assessments from the assertions
        ats = get_assessment_tracker_entries_by_user(db, user)
        # Get the assessment tracker ids from the user's assessments
        user_assessment_ids = [
            at.assessment_id for at in ats if at.status == "Approved"
        ]
        # Get the assessments that the user has completed
        assessments = [
            assessment
            for assessment in assessments
            if assessment.id not in user_assessment_ids
        ]

    return assessments


def get_assessment_by_name(db: Session, name: str) -> models.Assessments:
    """
    To get assessment by name.
    """
    assessment = db.query(models.Assessments).filter_by(name=name).first()
    return assessment


def get_assessment_by_id(db: Session, id: int) -> models.Assessments:
    """
    To get assessment by id.
    """
    assessment = db.query(models.Assessments).filter_by(id=id).first()
    return assessment


def get_badge_by_assessment_id(
    db: Session, assessment_id: int
) -> models.Badges:
    """
    To get badge by assessment id.
    """
    # Get the assessment name
    assessment = get_assessment_by_id(db, id=assessment_id)
    # Get the badge for the assessment based on the name
    badge = db.query(models.Badges).filter_by(name=assessment.name).first()
    return badge


# Get user by github username
def get_user_by_gh_username(db: Session, username: str) -> models.Users:
    """
    To get user by github username.
    """
    user = db.query(models.Users).filter_by(username=username).first()
    return user


# Function to update user info
def update_user_info(
    db: Session, update_data: dict, user: models.Users
) -> models.Users:
    """
    To update user info.
    """
    # For each key in the request data, update the user's info
    for key in update_data:
        setattr(user, key, update_data[key])

    db.commit()
    return user


# Function for adding the verification code to the user
def add_email_verification_code(
    db: Session,
    user: models.Users,
    verification_code: str,
    expires_at: datetime,
) -> models.Users:
    """
    To add email verification code to user.
    """
    user.email_verification_code = verification_code
    user.email_verification_code_expiry = expires_at
    db.commit()
    return user


# Get assertions
def get_assertions_by_user(db: Session, user: models.Users) -> list:
    """
    To get assertions.
    """
    # First get the assessment tracker entries for the user
    assessment_tracker = (
        db.query(models.AssessmentTracker).filter_by(user_id=user.id).all()
    )
    # Then get the assertions for each assessment tracker entry
    assertions = []
    for at in assessment_tracker:
        # Get the assertions for the assessment tracker entry
        at_assertions = (
            db.query(models.Assertions)
            .filter_by(assessment_tracker_id=at.id)
            .all()
        )
        # Add the assertions to the list
        assertions.extend(at_assertions)
    return assertions


def get_assessment_tracker_entry(
    db: Session, user_id: int, assessment_id: int
) -> models.AssessmentTracker:
    """
    To get assessment tracker entry.
    """
    # Get the assessment tracker entry
    at = (
        db.query(models.AssessmentTracker)
        .filter_by(user_id=user_id, assessment_id=assessment_id)
        .first()
    )
    return at


def get_assessment_tracker_entries_by_user(
    db: Session, user: models.Users
) -> list:
    """
    To get assessment tracker entries by user.
    """
    # Get the assessment tracker entries for the user
    assessment_tracker = (
        db.query(models.AssessmentTracker).filter_by(user_id=user.id).all()
    )
    return assessment_tracker
