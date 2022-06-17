import time
from utils import (
    sync_assertions,
    sync_assessments,
    download_releases_from_github,
    upload_releases_to_aws,
    sync_badges,
)
from config import settings
from db import db_session


def print_date_time():
    return time.strftime("%A, %d. %B %Y %I:%M:%S %p")


def flm(message):
    # make a nice log message with print_date_time
    log_message = f"\n[{print_date_time()}]: {message}\n"
    return log_message


def lambda_handler(event, context):
    """
    Handler for the lambda function.
    Will perform the following actions:
    1. Print the environment configuration
    2. Sync the assessments database from airtable
    3. Sync the badges from badgr
    4. Sync the assertions from badgr
    5. Sync the releases from github (code needed for launching new assessments)
    """

    if context:
        print("Lambda function ARN:", context.invoked_function_arn)
        print("CloudWatch log stream name:", context.log_stream_name)
        print("CloudWatch log group name:", context.log_group_name)
        print("Lambda Request ID:", context.aws_request_id)
        print(
            "Lambda function memory limits in MB:", context.memory_limit_in_mb
        )
        # We have added a 1 second delay so you can see the time remaining in get_remaining_time_in_millis.
        time.sleep(1)
        print(
            "Lambda time remaining in MS:",
            context.get_remaining_time_in_millis(),
        )

    # Run all sync functions
    print(flm("Starting sync"))

    print(flm("Syncing assessments..."))
    sync_assessments(settings=settings, db_session=db_session)

    print(flm("Syncing badges..."))
    sync_badges(settings=settings, db_session=db_session)

    print(flm("Syncing assertions..."))
    sync_assertions(settings=settings, db_session=db_session)

    print(flm("Syncing code - Downloading..."))
    download_releases_from_github(settings=settings, db_session=db_session)

    print(flm("Syncing code - Uploading..."))
    upload_releases_to_aws(settings=settings)

    print(flm("Syncing complete!"))


if __name__ == "__main__":
    lambda_handler(None, None)
