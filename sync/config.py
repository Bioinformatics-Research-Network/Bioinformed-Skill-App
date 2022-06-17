from pydantic import BaseSettings

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
    ACADEMIC_HONESTY_POLICY_URL: str
    CODE_OF_CONDUCT_URL: str
    MANDRILL_API_KEY: str
    EMAIL_VERIFICATION_EXPIRATION: int
    SITE_URL: str
    AIRTABLE_API_KEY: str
    AIRTABLE_BASE_ID: str
    BRN_API_URL: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_BUCKET: str
    AWS_REGION: str
    AWS_PUBLIC_S3_URL: str
    APPDATA_DIR: str


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
