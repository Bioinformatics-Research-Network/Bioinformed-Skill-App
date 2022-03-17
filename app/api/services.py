from app.db.session import SessionLocal

# to get local DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
