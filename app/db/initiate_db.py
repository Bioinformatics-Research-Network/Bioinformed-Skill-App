# Code for initializing database
# See https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/db/init_db.py
from app.db import session, base

# initialize database database
def init_db():
    return base.Base.metadata.create_all(bind=session.engine)



