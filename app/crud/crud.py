from app import models
from datetime import datetime
from sqlalchemy.orm import Session


# Create a function that retrieves all the assessments and their info
# from the database and returns them as a list of dictionaries.
def get_assessments(
    db: Session,
    language: list = None,
    types: list = None,
) -> list:
    """
    To get all assessments from the database.
    """
    assessments = db.query(models.Assessments).all()
    if language:
        assessments = [
            assessment for assessment in assessments if language in assessment.languages
        ]

    if types:
        assessments = [
            assessment for assessment in assessments if types in assessment.types
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


def get_badge_by_assessment_id(db: Session, assessment_id: int) -> models.Badges:
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


# Get reviewer by user id
def get_reviewer_by_user_id(db: Session, user_id: int) -> models.Reviewers:
    """
    To get reviewer by user id.
    """
    reviewer = db.query(models.Reviewers).filter_by(user_id=user_id).first()
    return reviewer


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


# Function to delete user
def delete_user(db: Session, user: models.Users) -> None:
    """
    To delete user.
    """
    # Check for foreign key constraints
    # Reviewer
    reviewer = db.query(models.Reviewers).filter_by(user_id=user.id).first()
    if reviewer:
        # Get the reviewer and delete it
        reviewer = get_reviewer_by_user_id(db, user.id)
        db.delete(reviewer)
        db.commit()
    # OAuth
    oauth = db.query(models.OAuth).filter_by(user_id=user.id).first()
    if oauth:
        db.delete(oauth)
        db.commit()
    # AssessmentTracker
    assessment_tracker = (
        db.query(models.AssessmentTracker).filter_by(user_id=user.id).all()
    )
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


# Function for adding the verification code to the user
def add_email_verification_code(
    db: Session, user: models.Users, verification_code: str, expires_at: datetime
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
        db.query(models.AssessmentTracker)
        .filter_by(user_id=user.id)
        .all()
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
    at = db.query(models.AssessmentTracker).filter_by(
        user_id=user_id, assessment_id=assessment_id
    ).first()
    return at
