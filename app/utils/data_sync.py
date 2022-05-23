import time
from app.config import Settings
from app import utils


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


# Write a function that syncs the badges table with the badgr API
def sync_badges(settings: Settings):
    # Get all badges from the badgr API
    # Issue badge
    bt = utils.get_bearer_token(settings)
    badges = utils.get_all_badges(bt, settings)
    print(badges)
    print(badges.json())
