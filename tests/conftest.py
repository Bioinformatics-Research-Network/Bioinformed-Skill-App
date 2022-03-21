# Sets the fixtures for running FastAPI and sqlalchemy tests
# See example: https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/tests/conftest.py

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from tests.utils.test_base import TestingSessionLocal
from app.main import app
from tests.utils.test_base import *

@pytest.fixture(scope="session")
def test_db_session() -> Generator:
    yield TestingSessionLocal()

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
  Create a clean database on every test case.
  For safety,abort if a test database already exists.
    """
    try:
        if database_exists(TEST_URL):
            drop_database(TEST_URL) #Test database already exists. Delete pre-existing db.
        create_database(TEST_URL)  # Create the test database.
        Base.metadata.create_all(bind=engine)  # Create the tables.
        app.dependency_overrides[get_db] = override_get_db # Mock the Dependency
        yield  # Run the tests.
    finally:
        drop_database(TEST_URL)  # Drop the test database.

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as client:
        yield client