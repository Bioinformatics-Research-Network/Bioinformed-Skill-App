from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# URL for database, can be changed as per requirements
SQLALCHEMY_DATABASE_URL = "sqlite:///./fake_skill_cert.db"

engine = create_engine(  # connect_args is required for SQLite
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# URL for database, can be changed as per requirements
SQLALCHEMY_DATABASE_URL_REAL = "sqlite:///./real_skill_cert.db"

realengine = create_engine(  # connect_args is required for SQLite
    SQLALCHEMY_DATABASE_URL_REAL, connect_args={"check_same_thread": False}
)

SessionLocalReal = sessionmaker(autocommit=False, autoflush=False, bind=realengine)
