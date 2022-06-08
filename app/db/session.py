from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Settings
from app.models import *
import os


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

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# Create the database tables
try:
    db.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(e)
    print("Error creating database tables")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
