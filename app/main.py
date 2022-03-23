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
@app.get("/")
def root(db: Session = Depends(get_db)):

    return {"Hello World!"}
