import os
from pydantic import BaseSettings


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


class Settings(BaseSettings):
    MANDRILL_API_KEY: str = os.environ.get("MANDRILL_API_KEY")
    RDS_ENDPOINT: str = os.environ.get("RDS_ENDPOINT")
    RDS_PORT: str = os.environ.get("RDS_PORT")
    RDS_DB_NAME: str = os.environ.get("RDS_DB_NAME")
    RDS_USERNAME: str = os.environ.get("RDS_USERNAME")
    RDS_PASSWORD: str = os.environ.get("RDS_PASSWORD")
    BADGR_CONFIG_PROD: dict = badgr_config_prod
    BADGR_CONFIG_TEST: dict = badgr_config_test
    BADGR_CONFIG: dict = badgr_config_prod
