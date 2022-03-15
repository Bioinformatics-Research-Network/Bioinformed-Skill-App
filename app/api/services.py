from app.db import base_class, session
from app.db.base_class import Base  
from app.models.models import Users, Reviewers, Assessment_Tracker, Assessments 
from app.db import base

# to get local DB
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database():
    return Base.metadata.create_all(bind=session.engine)