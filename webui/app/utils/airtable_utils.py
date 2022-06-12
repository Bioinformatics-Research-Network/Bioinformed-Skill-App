from pyairtable import Base
from app.config import settings

# function for getting the "users", "reviewers", and "assessments" tables
def get_at_assessments_table():
    # Get the airtable base
    base = Base(settings.AIRTABLE_API_KEY, settings.AIRTABLE_BASE_ID)
    # Get the "assessments" table
    assessments_table = base.get_table("assessments").all()
    return assessments_table
