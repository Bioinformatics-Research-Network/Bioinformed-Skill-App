from fastapi.testclient import TestClient
from app.crud.random_data_crud import *
from tests.utils.test_db import *
from app.db import base
from sqlalchemy.orm import Session
from app.api import services
from tests.api import test_services
import pytest


def test_root(client: TestClient, db: Session) -> None:

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == ["Hello World!"]
