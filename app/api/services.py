from app.db.session import SessionLocal


# to get local DB
def get_db():
    """
    Gets the local session for the local db, closes the db at the end of call.

    :yields: Generator object for the local session. finally closes the session.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
