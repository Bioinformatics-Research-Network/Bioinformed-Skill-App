# Sets the fixtures for running FastAPI and sqlalchemy tests

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from tests.utils import test_db
from main import app
from app.config import Settings
from app.api.services import get_settings


# Set Badgr test config
def get_settings_override():
    return Settings(BADGR_CONFIG=Settings().BADGR_CONFIG_TEST)


@pytest.fixture(scope="session")
def db() -> Generator:
    yield test_db.TestingSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as client:
        yield client
