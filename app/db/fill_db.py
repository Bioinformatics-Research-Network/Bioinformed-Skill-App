from sqlalchemy.orm import Session
from app.models import models
import csv


# Read from assessments.csv and get the data as a list of dictionaries
with open("app/db/assessments.csv", "r") as f:
    readr = csv.reader(f)
    next(readr)
    assessments = [
        {
            "orig_id": int(row[0]),
            "name": row[1],
            "description": row[2],
            "core_skill_areas": row[3],
            "languages": row[4],
            "types": row[5],
            "release_url": row[6],
            "prerequisites": row[7],
            "classroom_url": row[9],
        }
        for row in readr
    ]


def add_assessment(assessment_entry: dict, db: Session):
    """
    To add an assessment to the database.

    :param assessment_entry: dictionary of assessment data.
    :param db: database session.
    """

    # Check if already exists
    if db.query(models.Assessments).filter_by(name=assessment_entry["name"]).first():
        return

    db_obj = models.Assessments(
        orig_id=assessment_entry["orig_id"],
        name=assessment_entry["name"],
        description=assessment_entry["description"],
        core_skill_areas=assessment_entry["core_skill_areas"],
        languages=assessment_entry["languages"],
        types=assessment_entry["types"],
        release_url=assessment_entry["release_url"],
        prerequisites=assessment_entry["prerequisites"],
        classroom_url=assessment_entry["classroom_url"],
    )
    # Add the entry
    db.add(db_obj)
    db.commit()



def create_database(db: Session):
    """
    To create the database.
    """
    [add_assessment(assessment, db) for assessment in assessments]
    db.commit()
    db.close()

