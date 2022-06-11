from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from main import app
from app.dependencies import get_db
from app.db.models import Base
from app.crud import random_data_crud
import random

random.seed(42)

TEST_URL = "sqlite:///./test.db"

engine = create_engine(TEST_URL, connect_args={"check_same_thread": False}, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def create_random_data(db: Session):
    random_data_crud.create_random_user(db=db, random_users=5)
    random_data_crud.create_random_reviewers(db=db, random_reviewers=5)
    random_data_crud.create_assessments(db=db)
    random_data_crud.create_random_assessment_tracker(
        db=db, random_assessment_tracker=5
    )
