# FastAPI should be called here
# Global Security should go here -- see https://fastapi.tiangolo.com/tutorial/security/first-steps/

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.init_db import init
from app.api.services import get_db

app = FastAPI()

# initialize database : used here to initialize fke database
init()

# root was created to test if the api works
@app.get("/")
def random_data(db: Session = Depends(get_db)):

    return {"Working"}
