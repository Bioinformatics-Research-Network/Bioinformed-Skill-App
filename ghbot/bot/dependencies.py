import os
from functools import lru_cache
from pydantic import BaseSettings
from github import GithubIntegration
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Base URL for the GitHub API
gh_url = "https://api.github.com"

# Base HTTP URL for GitHub.com
gh_http = "https://github.com"

# Header for the GitHub API
accept_header = "application/vnd.github.v3+json"

# Filename for all actions workflows
workflow_filename = "checks.yml"

# ref for all trainee git
git_ref = "main"

# Admin usernames
admins = ["millerh1", "itchytummy", "bioresnet"]

# Dict of valid App install IDs
if (
    os.environ.get("APP_ENV") == "production"
    or os.environ.get("APP_ENV") == "development"
):
    installation_ids = {
        "Skill Assessment Tutorial (Python)": 25630785,
        "Skill Assessment Tutorial (R)": 25901888,
        "Python Programming I": 25616884,
        "R Programming I": 25958132,
        "Python Programming II": 25476585,
        "R Programming II": 25520792,
        "Test": 25533349,
    }
    BADGE_IDs = {
        "Skill Assessment Tutorial (R)": "zS91nadxSQCchE_ahLFgvw",
        "Skill Assessment Tutorial (Python)": "MMuVRwluTd6cI33-0ILs3w",
        "Python Programming I": "rfT_GJApRoavmHi_TemqqQ",
        "Python Programming II": "5xCf5xpRQqOhRCykbITuLA",
        "R Programming I": "v0CU877hR5qI8OtDN7EYTg",
        "R Programming II": "h3lCNmoHRjmqNI5D5Q6a-g",
        "Test": "OcVxPZEORASs4dBL0h5mOw",
    }
    # file for storing temporary access tokens
    token_fp = "access_tokens.json"
else:
    installation_ids = {
        "Test": 26363998,
    }
    BADGE_IDs = {
        "Test": "OcVxPZEORASs4dBL0h5mOw",
    }
    # file for storing temporary access tokens
    token_fp = "access_tokens.dev.json"

# Dict of valid commands
cmds = ["hello", "help", "review", "approve"]
cmds_descriptions = {
    "hello": "Say hello",
    "help": "Show this help message",
    "review": (
        "For skill assessments which require manual review, this"
        + " command will trigger the review process."
    ),
    "approve": (
        "For skill assessments which require manual review, this"
        + " command is available to reviewers to approve the"
        + " assessment and issue a badge."
    ),
}


# Get secrets
class Settings(BaseSettings):
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_BUCKET: str
    AWS_REGION: str
    CRUD_APP_URL: str
    BOT_KEY_PATH: str
    APP_ID: int
    APP_ENV_NAME: str
    RDS_ENDPOINT: str
    RDS_PORT: str
    RDS_DB_NAME: str
    RDS_USERNAME: str
    RDS_PASSWORD: str


@lru_cache()
def get_settings():
    print(os.environ.get("APP_ENV"))
    if os.environ.get("APP_ENV") == "development":
        print("Loading development settings")
        settings = Settings(_env_file=".dev.env", _env_file_encoding="utf-8")
    elif os.environ.get("APP_ENV") == "production":
        print("Loading production settings")
        settings = Settings(_env_file=".prod.env", _env_file_encoding="utf-8")
    elif os.environ.get("APP_ENV") == "testing":
        print("Loading testing settings")
        settings = Settings(_env_file=".test.env", _env_file_encoding="utf-8")
    else:  # pragma: no cover
        print("Loading default settings (testing)")
        settings = Settings(_env_file=".test.env", _env_file_encoding="utf-8")
    return settings


settings = get_settings()

# Read the bot certificate
try:
    # This will work when BOT_KEY is set in the environment
    app_key = os.environ["BOT_KEY"]
except KeyError:  # pragma: no cover
    # This will work when the key comes from a file (not in ENV)
    with open(
        os.path.normpath(os.path.expanduser(settings.BOT_KEY_PATH)), "r"
    ) as cert_file:
        app_key = cert_file.read()


# Create a GitHub integration instance
git_integration = GithubIntegration(
    integration_id=settings.APP_ID, private_key=app_key
)


# URL for database, can be changed as per requirements
SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://"
    + settings.RDS_USERNAME
    + ":"
    + settings.RDS_PASSWORD
    + "@"
    + settings.RDS_ENDPOINT
    + ":"
    + settings.RDS_PORT
    + "/"
    + settings.RDS_DB_NAME
)

# Create DB engine and get local session
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# to get local DB
def get_db():
    """
    Gets the local session for the local db, closes the db at the end of call.

    :yields: Generator object for the local session. finally closes the session.
    """
    try:  # pragma: no cover
        db = SessionLocal()
        yield db
    finally:
        db.close()


