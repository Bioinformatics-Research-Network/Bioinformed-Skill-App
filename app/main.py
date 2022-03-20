# FastAPI should be called here
# Global Security should go here -- see https://fastapi.tiangolo.com/tutorial/security/first-steps/

from fastapi import FastAPI , Depends
from sqlalchemy.orm import Session
from app.db.init_db import init
from app.db.session import SessionLocal
from app.tests.crud.crud import *
from api.services import get_db

app = FastAPI()

# initialize database : used here to initialize fke database
init()

@app.get("/")
def random_data(db: Session=Depends(get_db)):
    # create_random_user(100, db=db)
    # create_random_reviewers(20, db=db)
    return {"Working"}



