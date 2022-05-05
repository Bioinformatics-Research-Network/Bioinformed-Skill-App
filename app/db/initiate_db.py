# Code for initializing database
from app.db.base_class import Base
from app.db import session


# initialize database database
def init_db():
    """
    Initiates the database, creates new database if it doesn't exist.
    Invoked in app/main.py 

    :returns: None 
    """
    return Base.metadata.create_all(bind=session.engine)
