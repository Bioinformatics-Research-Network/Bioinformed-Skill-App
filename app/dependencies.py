from functools import lru_cache
from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.db.models import Base
from app.db.test_data import test_users, test_reviewers, test_assessments, test_at, test_badges
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
    GITHUB_BOT_URL: str



@lru_cache()
def get_settings():
    # Set the config based on the environment
    if os.environ.get("APP_ENV") == "development": # pragma: no cover
        print("Loading development settings")
        settings = Settings(_env_file=".dev.env", _env_file_encoding="utf-8")
    elif os.environ.get("APP_ENV") == "production": # pragma: no cover
        print("Loading production settings")
        settings = Settings(_env_file=".prod.env", _env_file_encoding="utf-8")
    elif os.environ.get("APP_ENV") == "testing": # pragma: no cover
        print("Loading testing settings")
        settings = Settings(_env_file=".test.env", _env_file_encoding="utf-8")
    else: # pragma: no cover
        print("Loading default settings (testing)")
        settings = Settings(_env_file=".test.env", _env_file_encoding="utf-8")
    return settings


# Get settings
settings = get_settings()

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

# If testing, delete and then create the database
if os.environ.get("APP_ENV") == "testing": # pragma: no cover
    # Drop all tables
    Base.metadata.drop_all(engine)
    # Create all tables
    Base.metadata.create_all(engine)
    # Create all tables tests/test_data.py
    with SessionLocal() as session:
        session.add_all(test_users)
        session.commit()
        session.add_all(test_reviewers)
        session.commit()
        session.add_all(test_assessments)
        session.commit()
        session.add_all(test_at)
        session.commit()
        session.add_all(test_badges)
        session.commit()


# to get local DB
def get_db():
    """
    Gets the local session for the local db, closes the db at the end of call.

    :yields: Generator object for the local session. finally closes the session.
    """
    try: # pragma: no cover
        db = SessionLocal()
        yield db
    finally:
        db.close()
