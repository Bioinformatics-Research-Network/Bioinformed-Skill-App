from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.services import get_db
from sqlalchemy.ext.declarative import declarative_base
from app.db import base

TEST_URL = "sqlite:///./tests/test.db"

engine = create_engine(
    TEST_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


base.Base.metadata.create_all(bind=engine)



