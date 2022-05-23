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
    ## Check for foreign key constraints
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
                print(assertions)
                db.delete(assertions)
                db.commit()
            # Delete assessment tracker entry
            db.delete(at)
            db.commit()

    ## Delete user
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
