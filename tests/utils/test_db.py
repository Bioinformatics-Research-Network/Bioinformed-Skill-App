from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.services import get_db
from sqlalchemy.ext.declarative import declarative_base
from app.db import base
import contextlib
from app.crud.random_data_crud import *


TEST_URL = "sqlite:///./test.db"

engine = create_engine(TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


base.Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
        
    finally:
        db.close()



app.dependency_overrides[get_db] = override_get_db

def create_random_data(
    db: Session
    ):
    create_random_user(db=db, random_users=5)
    create_random_reviewers(db=db, random_reviewers=5)
    create_assessments(db=db, random_assessments=5)
    create_random_assessment_tracker(db=db, random_assessment_tracker=5)




