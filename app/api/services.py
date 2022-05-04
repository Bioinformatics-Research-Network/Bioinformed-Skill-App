from app.db.session import SessionLocal


# to get local DB
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
