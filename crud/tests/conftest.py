# Sets the fixtures for running FastAPI and sqlalchemy tests

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from main import app
from app.dependencies import get_db, get_settings, Settings


# Set Badgr test config
def get_settings_override():
    return Settings(
        _env_file=".test.env",
        _env_file_encoding="utf-8",
    )


@pytest.fixture(scope="session")
def db():
    db = next(get_db())
    yield db


@pytest.fixture(scope="module")
def client() -> Generator:
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as client:
        yield client

