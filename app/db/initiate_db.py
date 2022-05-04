# Code for initializing database
from app.db.base_class import Base
from app.db import session


# initialize database database
def init_db():
    return Base.metadata.create_all(bind=session.engine)
