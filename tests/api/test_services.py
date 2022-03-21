from tests.utils.test_db import *

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()