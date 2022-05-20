from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app.config import RDS_DB_NAME, RDS_ENDPOINT, RDS_PASSWORD, RDS_PORT, RDS_USERNAME

# URL for database, can be changed as per requirements
SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://" + RDS_USERNAME + ":" + RDS_PASSWORD + 
    "@" + RDS_ENDPOINT +  ":" + RDS_PORT + "/" + RDS_DB_NAME
)

engine = create_engine(SQLALCHEMY_DATABASE_URI)
if not database_exists(engine.url): # pragma: no cover
    create_database(engine.url)     # Create new DB    
    print("New Database Created") # Verifies if database is there or not.
else: # pragma: no cover
    print("Database Already Exists")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SessionLocal().execute("DROP DATABASE IF EXISTS `skill-db`")
