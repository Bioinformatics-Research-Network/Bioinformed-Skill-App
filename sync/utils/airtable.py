from models import Assessments
from config import Settings
from pyairtable import Base as at_base
from sqlalchemy.orm import Session


# function for getting the "users", "reviewers", and "assessments" tables
def get_at_assessments_table(settings: Settings):
    # Get the airtable base
    base = at_base(settings.AIRTABLE_API_KEY, settings.AIRTABLE_BASE_ID)
    # Get the "assessments" table
    assessments_table = base.get_table("assessments").all()
    return assessments_table


def sync_assessments(settings: Settings, db_session: Session):
    # Get the assessments from the Airtable API
    assessmentlst = get_at_assessments_table(settings)

    # Loop through all assessments and
    # If they don't exist in the database, add them
    # If they do exist, update them
    try:
        for assessment in assessmentlst:

            # Check if the assessment already exists in the database
            current_assessment = db_session.query(Assessments).filter_by(
                id=assessment["fields"]["id"]
            )

            # Wrangle the fields to be compatible with the schema
            # fields = utils.wrangle_assessment(assessment)
            fields = assessment["fields"]

            # For all fields that are a list, convert them to strings separated by commas
            fields = {
                k: (",".join(v) if isinstance(v, list) else v)
                for k, v in fields.items()
            }

            if current_assessment.first() is None:
                print(
                    "Assessment does not exist in database:  "
                    + str(assessment["fields"]["name"])
                    + " - "
                    + str(assessment["fields"]["id"])
                )
                assessment = Assessments(**fields)
                db_session.add(assessment)
                db_session.commit()
            else:
                print(
                    "Assessment already exists -- updating: "
                    + str(assessment["fields"]["name"])
                    + " - "
                    + str(assessment["fields"]["id"])
                )
                # Update the assessment in the database
                current_assessment.update(values=fields)
                db_session.commit()
    except Exception as e:
        print(str(e))
        # Rollback the changes to the database
        db_session.rollback()
        raise e

    return True
