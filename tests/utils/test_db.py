from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.services import get_db
from sqlalchemy.ext.declarative import declarative_base
from app.db import base
import contextlib


TEST_URL = "sqlite:///./test.db"

engine = create_engine(TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


base.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()



app.dependency_overrides[get_db] = override_get_db

# deteling test db tables at end of the test session
# meta = MetaData()
# with contextlib.closing(engine.connect()) as con:
#     trans = con.begin()
#     for table in reversed(meta.sorted_tables):
#         con.execute(table.delete())
#     trans.commit()
