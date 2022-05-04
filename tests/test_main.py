from fastapi.testclient import TestClient
from tests.utils import test_db
from sqlalchemy.orm import Session


def test_root(client: TestClient, db: Session) -> None:
    test_db.create_random_data(db=db)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == ["Hello World!"]
