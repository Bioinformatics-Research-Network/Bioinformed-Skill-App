# Code for initializing database
# See https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/db/init_db.py
from sqlalchemy.orm import Session
from app.db import session
from app.db import base

# initialize database database
def init_db(db: Session):
    base.Base.metadata.create_all(bind=session.engine)