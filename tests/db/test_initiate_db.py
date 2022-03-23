from app.db import session, base
from tests.utils import test_db
from app.db import initiate_db

# initialize database database
def test_init_db():
    assert initiate_db.init_db() == None
