from app.config import Settings
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
import os


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
