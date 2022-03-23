# FastAPI should be called here
# Global Security should go here -- see https://fastapi.tiangolo.com/tutorial/security/first-steps/

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.initiate_db import init_db
from app.api.services import get_db
from app.crud.random_data_crud import *
from app.db import base

app = FastAPI()

# initialize database : used here to initialize fake data in database
init_db()

# root was created to test if the api works
@app.get("/create_random_data")
def random_data(db: Session = Depends(get_db)):

    create_random_user(db=db, random_users=100)
    create_random_reviewers(db=db, random_reviewers=20)
    create_assessments(db=db, random_assessments=10)
    create_random_assessment_tracker(db=db, random_assessment_tracker=10)

    return {"Working"}
