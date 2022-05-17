from app import models

# Create a function that retrieves all the assessments and their info
# from the database and returns them as a list of dictionaries.
def get_assessments(
    db: models.db.Session, 
    language: list = None, 
    types: list = None, 
) -> list:
    """
    To get all assessments from the database.
    """
    assessments = db.query(models.Assessments).all()
    if language:
        assessments = [
            assessment
            for assessment in assessments
            if language in assessment.languages
        ]
        
    if types:
        assessments = [
            assessment
            for assessment in assessments
            if types in assessment.types
        ]
    return assessments

