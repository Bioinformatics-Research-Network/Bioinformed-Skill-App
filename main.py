# FastAPI should be called here
# Global Security should go here -- see https://fastapi.tiangolo.com/tutorial/security/first-steps/

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.api.services import get_db
from app.api import api_endpoints


app = FastAPI()


@app.get("/")
def root(db: Session = Depends(get_db)):
    """
    Root api endpoint, has no specific function. Was created to test API.

    :param db: Generator for Session of database

    :returns: json with "Hello World!"
    """
    return {"Hello World!"}


# Router links all the api endpoints to main.py
app.include_router(api_endpoints.router)
