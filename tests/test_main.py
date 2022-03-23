from fastapi.testclient import TestClient
from fastapi import Depends
from app.crud.random_data_crud import *
from tests.utils.test_db import *
from app.db import base
from sqlalchemy.orm import Session
from app.api import services
from tests.api import test_services
import pytest


def test_random_data(client: TestClient, db: Session) -> None:

    r = client.get("/create_random_data")
    assert r.status_code == 200
    assert r.json() == ["Working"]
