import pytest
from app.api.services import get_db

def test_get_db():
    db = get_db()
    assert db.__class__.__name__ == 'generator'
    assert next(db).__class__.__name__ == 'Session'

