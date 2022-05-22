from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app.config import Settings

settings = Settings(_env_file=".prod.env", _env_file_encoding="utf-8")

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

engine = create_engine(SQLALCHEMY_DATABASE_URI)
if not database_exists(engine.url):  # pragma: no cover
    create_database(engine.url)  # Create new DB
    print("New Database Created")  # Verifies if database is there or not.
else:  # pragma: no cover
    print("Database Already Exists")


# Create the database tables
from app.db.base_class import Base
from app.models import *

db.Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

## This will delete all the data in the database
# SessionLocal().execute("DROP DATABASE IF EXISTS `skill-db`")
