from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.main import app
from app.api.services import get_db
import pytest
from sqlalchemy_utils import (database_exists,
                            create_database,
                            drop_database)

TEST_URL = "sqlite:///./tests/test.db"

engine = create_engine(
    TEST_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


