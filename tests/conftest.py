# Sets the fixtures for running FastAPI and sqlalchemy tests

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from tests.utils import test_db
from app.main import app


@pytest.fixture(scope="session")
def db() -> Generator:
    yield test_db.TestingSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as client:
        yield client
