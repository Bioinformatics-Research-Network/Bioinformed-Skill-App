from pydantic import BaseSettings
import os

BADGE_IDs = {
    "Skill Assessment Tutorial (R)": "zS91nadxSQCchE_ahLFgvw",
    "Skill Assessment Tutorial (Python)": "MMuVRwluTd6cI33-0ILs3w",
    "Python Programming I": "rfT_GJApRoavmHi_TemqqQ",
    "Python Programming II": "5xCf5xpRQqOhRCykbITuLA",
    "R Programming I": "v0CU877hR5qI8OtDN7EYTg",
    "R Programming II": "h3lCNmoHRjmqNI5D5Q6a-g",
    "Test": "OcVxPZEORASs4dBL0h5mOw",
}


class Settings(BaseSettings):
    RDS_ENDPOINT: str
    RDS_PORT: str
    RDS_DB_NAME: str
    RDS_USERNAME: str
    RDS_PASSWORD: str
    BADGR_USERNAME: str
    BADGR_PASSWORD: str
    BADGR_BASE_URL: str
    BADGR_SCOPE: str
    BADGR_ISSUER_ID: str
    BADGR_GRANT_TYPE: str
    BADGR_CLIENT_ID: str
    BADGE_IDs: dict = BADGE_IDs
    FLASK_APP_SECRET_KEY: str
    GH_OAUTH_CLIENT_ID: str
    GH_OAUTH_CLIENT_SECRET: str
    PRIVACY_POLICY_URL: str
    MANDRILL_API_KEY: str
    EMAIL_VERIFICATION_EXPIRATION: int
    SITE_URL: str


if os.environ.get("FLASK_ENV") == "development":
    settings = Settings(_env_file=".dev.env", _env_file_encoding="utf-8")
elif os.environ.get("FLASK_ENV") == "production":
    settings = Settings(_env_file=".prod.env", _env_file_encoding="utf-8")
else:
    settings = Settings(_env_file=".dev.env", _env_file_encoding="utf-8")
