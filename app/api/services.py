from app.db import base_class, session


# to get local DB
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create database
def create_database():
    return base_class.Base.metadata.create_all(bind=session.engine)