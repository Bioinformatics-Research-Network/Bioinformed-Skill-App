import shutil
import os
import urllib
import boto3
import mimetypes

from config import Settings
from models import Assessments
from sqlalchemy.orm import Session


def download_releases_from_github(settings: Settings, db_session: Session):
    # Get list of releases from the assessments database table using sqlalchemy
    # Filter the query to only include rows where the latest_release is not null
    releases = db_session.query(Assessments).filter(
        Assessments.latest_release != None
    )
    appdatadir = settings.APPDATA_DIR
    # Delete the "{appdatadir}/" directory if it exists
    if os.path.exists(f"{appdatadir}/"):
        shutil.rmtree(f"{appdatadir}/")

    # From the list of releases, get the latest_release and template_repo fields
    for release in releases:
        print("Downloading release: " + release.name)
        release_url = f"https://api.github.com/repos/Bioinformatics-Research-Network/{release.template_repo}/zipball/{release.latest_release}"
        print(release_url)
        # Creat the download folder if it doesn't exist
        download_folder = (
            f"{appdatadir}/tmp/{release.template_repo}/{release.latest_release}"
        )
        output_folder = (
            f"{appdatadir}/{release.template_repo}/{release.latest_release}"
        )
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        else:
            shutil.rmtree(output_folder)
            os.makedirs(output_folder)
        # Download the release from github and save it to the downloads folder using urllib
        urllib.request.urlretrieve(release_url, f"{download_folder}/tmp.zip")
        # Unzip the file such that the contents are in the download folder
        os.system(f"unzip {download_folder}/tmp.zip -d {download_folder}")
        # Delete the zip file
        os.remove(f"{download_folder}/tmp.zip")
        # Find the directory inside the zip file
        wlk = os.walk(download_folder)
        directory = next(wlk)[1]
        # Move that directory up one level to the download folder
        os.rename(f"{download_folder}/{directory[0]}", output_folder)
        # Delete the download folder, including the top level directory
        shutil.rmtree(download_folder)
        # Delete the tmp/ directory
        shutil.rmtree(f"{appdatadir}/tmp")


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
    path = f"{settings.APPDATA_DIR}/"
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
