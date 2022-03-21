from tests.utils.test_db import *

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()