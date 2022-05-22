from app.db.session import SessionLocal
from functools import lru_cache
from app.config import Settings

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


@lru_cache()
def get_settings():
    return Settings(
        _env_file=".prod.env", _env_file_encoding="utf-8"
    )  # pragma: no cover
