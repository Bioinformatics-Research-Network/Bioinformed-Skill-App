# Sets the fixtures for running FastAPI and sqlalchemy tests

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from main import app

from app.dependencies import engine, SessionLocal
from app.db.test_data import test_users, test_reviewers, test_assessments, test_at, test_badges
from app.db.models import Base
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


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    print("Session start")
    # Drop all tables
    Base.metadata.drop_all(engine)
    # Create all tables
    Base.metadata.create_all(engine)
    # Create all tables tests/test_data.py
    with SessionLocal() as session:
        session.add_all(test_users)
        session.commit()
        session.add_all(test_reviewers)
        session.commit()
        session.add_all(test_assessments)
        session.commit()
        session.add_all(test_at)
        session.commit()
        session.add_all(test_badges)
        session.commit()
