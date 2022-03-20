import app
from app.api.services import get_db

def test_getdb():
    db=get_db()
    assert db.__class__.__name__ == "generator"
