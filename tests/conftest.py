# Sets the fixtures for running FastAPI and sqlalchemy tests
# See example: https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/tests/conftest.py

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from tests.utils.test_db import *
from app.main import app
from app.utils.random_data_utils import *
from sqlalchemy.orm import Session

@pytest.fixture(scope="session")
def db() -> Generator:
    yield TestingSessionLocal()
        
@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as client:
        yield client