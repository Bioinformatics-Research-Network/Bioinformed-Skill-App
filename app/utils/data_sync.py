from dataclasses import field
import time
from app.config import Settings
from app import utils
from app.models.models import Badges, Assertions
from app.db import db_session


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


# Write a function that syncs the badges table with the badgr API
def sync_badges(settings: Settings):
    # Get all badges from the badgr API
    bt = utils.get_bearer_token(settings)
    try:
        badges = utils.get_all_badges(bt, settings)
        badgelst = badges.json()['result']
    except Exception as e:
        print(str(e))
        raise e

    # Loop through all badges and add them to the badges table
    try:
        for badge in badgelst:
            print(badge['name'])

            # Check if the badge already exists in the database
            current_badge = db_session.query(Badges).filter_by(name=badge['name'])

            # Convert all the fields to strings using dict comprehension
            fields = {k: str(v) for k, v in badge.items()}

            if current_badge.first() is None:
                print("Badge does not exist in database")
                badge = Badges(**fields)
                db_session.add(badge)
                db_session.commit()
            else:
                print('Badge already exists -- updating')
                # Update the badge in the database
                current_badge.update(values=fields)
                db_session.commit()
    except Exception as e:
        print(str(e))
        # Rollback the changes to the database
        db_session.rollback()
        raise e


def sync_assertions(settings: Settings):
    # Get all assertions from the badgr API
    bt = utils.get_bearer_token(settings)
    try:
        assertions = utils.get_all_assertions(bt, settings)
        assertionlst = assertions.json()['result']
    except Exception as e:
        print(str(e))
        raise e
    
    # Loop through all assertions and add them to the assertions table
    try:
        for assertion in assertionlst:

            # Check if the assertion already exists in the database
            current_assertion = db_session.query(Assertions).filter_by(entityId=assertion['entityId'])

            # Wrangle the fields to be compatible with the schema
            fields = utils.wrangle_assertion(assertion)

            if current_assertion.first() is None:
                print("Assertion does not exist in database")
                assertion = Assertions(**fields)
                db_session.add(assertion)
                db_session.commit()
            else:
                print('Assertion already exists -- updating')
                # Update the assertion in the database
                current_assertion.update(values=fields)
                db_session.commit()
    except Exception as e:
        print(str(e))
        # Rollback the changes to the database
        db_session.rollback()
        raise e

