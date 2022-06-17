import time
from app.config import Settings
from app import utils
from app.models.models import Badges, Assertions, Assessments
from app.db import db_session

import boto3


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


# Write a function that syncs the badges table with the badgr API
def sync_badges(settings: Settings):
    # Get all badges from the badgr API
    bt = utils.get_bearer_token(settings)
    try:
        badges = utils.get_all_badges(bt, settings)
        badgelst = badges.json()["result"]
    except Exception as e:
        print(str(e))
        raise e

    # Loop through all badges and add them to the badges table
    try:
        for badge in badgelst:
            print(badge["name"])

            # Check if the badge already exists in the database
            current_badge = db_session.query(Badges).filter_by(
                name=badge["name"]
            )

            # Convert all the fields to strings using dict comprehension
            fields = {k: str(v) for k, v in badge.items()}

            if current_badge.first() is None:
                print("Badge does not exist in database")
                badge = Badges(**fields)
                db_session.add(badge)
                db_session.commit()
            else:
                print("Badge already exists -- updating")
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
        assertionlst = assertions.json()["result"]
    except Exception as e:
        print(str(e))
        raise e

    # Loop through all assertions and add them to the assertions table
    try:
        for assertion in assertionlst:

            # Check if the assertion already exists in the database
            current_assertion = db_session.query(Assertions).filter_by(
                entityId=assertion["entityId"]
            )

            # Wrangle the fields to be compatible with the schema
            fields = utils.wrangle_assertion(assertion)

            if current_assertion.first() is None:
                print("Assertion does not exist in database")
                assertion = Assertions(**fields)
                db_session.add(assertion)
                db_session.commit()
            else:
                print("Assertion already exists -- updating")
                # Update the assertion in the database
                current_assertion.update(values=fields)
                db_session.commit()
    except Exception as e:
        print(str(e))
        # Rollback the changes to the database
        db_session.rollback()
        raise e


def sync_assessments():
    # Get the assessments from the Airtable API
    assessmentlst = utils.get_at_assessments_table()

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


import urllib
import os
import shutil


def download_releases_from_github(settings: Settings):
    # Get list of releases from the assessments database table using sqlalchemy
    # Filter the query to only include rows where the latest_release is not null
    releases = db_session.query(Assessments).filter(
        Assessments.latest_release != None
    )
    # Delete the "../appdata/" directory if it exists
    if os.path.exists("../appdata/"):
        shutil.rmtree("../appdata/")

    # From the list of releases, get the latest_release and template_repo fields
    for release in releases:
        print("Downloading release: " + release.name)
        release_url = f"https://api.github.com/repos/Bioinformatics-Research-Network/{release.template_repo}/zipball/{release.latest_release}"
        print(release_url)
        # Creat the download folder if it doesn't exist
        download_folder = (
            f"../appdata/tmp/{release.template_repo}/{release.latest_release}"
        )
        output_folder = (
            f"../appdata/{release.template_repo}/{release.latest_release}"
        )
        print(download_folder)
        print(output_folder)
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # Download the release from github and save it to the downloads folder using urllib
        urllib.request.urlretrieve(release_url, f"{download_folder}/tmp.zip")
        # Unzip the file such that the contents are in the download folder
        os.system(f"unzip {download_folder}/tmp.zip -d {download_folder}")
        # Delete the zip file
        os.remove(f"{download_folder}/tmp.zip")
        # Find the directory inside the zip file
        wlk = os.walk(download_folder)
        print(wlk)
        directory = next(wlk)[1]
        print(directory)
        # Move that directory up one level to the download folder
        os.rename(f"{download_folder}/{directory[0]}", output_folder)
        # Delete the download folder, including the top level directory
        shutil.rmtree(download_folder)
        # Delete the tmp/ directory
        shutil.rmtree("../appdata/tmp")


import mimetypes


def upload_releases_to_aws(settings: Settings):
    # Configure s3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name=settings.AWS_REGION,
    )

    # For all the directories in the appdata folder, upload them to S3
    # This should preserve the directory structure
    path = "../appdata/"
    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            file_mime = mimetypes.guess_type(file)[0] or "binary/octet-stream"
            key = "templates/" + full_path[len(path) :]
            print(key)
            with open(full_path, "rb") as data:
                s3.put_object(
                    Key=key,
                    Body=data,
                    ContentType=file_mime,
                    Bucket=settings.AWS_BUCKET,
                )
            # Make sure the file is publically accessible

    # s3.put_object_acl(ACL='public-read', Bucket=settings.AWS_BUCKET, Key=key)
