from app.db import session
from app.db import base

# to get local DB
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database():
    return session.Base.metadata.create_all(bind=session.engine)