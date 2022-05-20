# Contains the configuration for the app
# See example:
# https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/core/config.py

import os

# API key for Mandrill (email transactions)
MANDRILL_API_KEY = os.environ.get("MANDRILL_API_KEY")

# Config for Badgr
badgr_config_prod = {
    "BADGR_USERNAME": os.environ.get("BADGR_USERNAME"),
    "BADGR_PASSWORD": os.environ.get("BADGR_PASSWORD"),
    "BADGR_BASE_URL": "https://api.badgr.io",
    "BADGR_SCOPE": "rw:issuer rw:backpack",
    "BADGR_ISSUER_ID": "ZXuOnkDGSiC25nylSKfweA",
    "BADGR_GRANT_TYPE": "password",
    "BADGR_CLIENT_ID": "public",
    "BADGE_IDs": {
        "Python Programming I": "rfT_GJApRoavmHi_TemqqQ",
        "Python Programming II": "5xCf5xpRQqOhRCykbITuLA",
        "R Programming I": "v0CU877hR5qI8OtDN7EYTg",
        "R Programming II": "h3lCNmoHRjmqNI5D5Q6a-g",
    },
}

badgr_config_test = {
    "BADGR_USERNAME": os.environ.get("BADGR_TEST_USERNAME"),
    "BADGR_PASSWORD": os.environ.get("BADGR_TEST_PASSWORD"),
    "BADGR_BASE_URL": "https://api.test.badgr.com",
    "BADGR_SCOPE": "rw:issuer rw:backpack",
    "BADGR_ISSUER_ID": "4aQWejKFThS1NtViZk6GnQ",
    "BADGR_GRANT_TYPE": "password",
    "BADGR_CLIENT_ID": "public",
    "BADGE_IDs": {
        "Python Programming I": "OcVxPZEORASs4dBL0h5mOw",
        "Python Programming II": "OcVxPZEORASs4dBL0h5mOw",
        "R Programming I": "OcVxPZEORASs4dBL0h5mOw",
        "R Programming II": "OcVxPZEORASs4dBL0h5mOw",
        "ChIP-Seq Analysis": "OcVxPZEORASs4dBL0h5mOw",
        "Test": "OcVxPZEORASs4dBL0h5mOw",
    },
}

# Connection details for RDS
RDS_ENDPOINT = os.environ.get("RDS_ENDPOINT")
RDS_PORT = os.environ.get("RDS_PORT")
RDS_DB_NAME = os.environ.get("RDS_DB_NAME")
RDS_USERNAME = os.environ.get("RDS_USERNAME")
RDS_PASSWORD = os.environ.get("RDS_PASSWORD")


