# Sets the fixtures for running FastAPI and sqlalchemy tests
# See example: https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/tests/conftest.py

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from app.db import initiate_db
from tests.utils.test_db import *
from app.main import app
from app.crud.random_data_crud import *


@pytest.fixture(scope="session")
def db() -> Generator:
    yield TestingSessionLocal()

@pytest.fixture
def create_random_data(
    db: Session
    ):
    create_random_user(db=db, random_users=100)
    create_random_reviewers(db=db, random_reviewers=25)
    create_assessments(db=db, random_assessments=10)
    create_random_assessment_tracker(db=db, random_assessment_tracker=20)

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as client:
        yield client
