from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.main import app
from app.api.services import get_db
import pytest
from tests.api.test_services import override_get_db

TEST_URL = "sqlite:///./tests/test.db"

engine = create_engine(
    TEST_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)



app.dependency_overrides[get_db] = override_get_db

