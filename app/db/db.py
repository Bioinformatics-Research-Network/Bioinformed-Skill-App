from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import config


# URL for database, can be changed as per requirements
SQLALCHEMY_DATABASE_URL = config.SQLALCHEMY_DATABASE_URI

engine = create_engine(  # connect_args is required for SQLite
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
